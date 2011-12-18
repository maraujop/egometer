#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import re
from optparse import OptionParser
from datetime import datetime
from pprint import pprint

try:
    import requests
    from oauth_hook import OAuthHook
except ImportError:
    sys.stderr.write('You need to install requests and requests-oauth, you can do so running `pip install requests requests-oauth`\n')
    sys.exit(1)

try:
    import simplejson as json
except ImportError:
    import json

from exception import TwitterAPIException, TwitterException
from settings import (
    TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET,
    TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET
)


def remaining_calls_from_response(response_headers):
    """
    Returns an integer with the number of remaining calls available to the API, 
    extracts this information from the response headers
    """
    if 'x-ratelimit-remaining' in response_headers:
        return int(response_headers['x-ratelimit-remaining'])

# WITHOUT MATCHING
AT_SIGNS = ur'[@\uff20]'
LIST_END_CHARS = ur'([a-z0-9_]{1,20})(/[a-z][a-z0-9\x80-\xFF-]{0,79})?'
USERNAME_REGEX = re.compile(ur'^(' + AT_SIGNS + LIST_END_CHARS + '\s)*', re.IGNORECASE) 
def tweet_replies(tweet):
    """
    Returns a list of users that the tweet text replies to, without @ symbols::

        "@user1 @user2 blablabla /cc @user3" -> ['user1', 'user2']
    """ 
    return [username.strip('@') for username in USERNAME_REGEX.match(tweet).group(0).split()]

def retweet_replies_user(retweet, user_screen_name):
    """
    Returns True if `retweet` replies to `user_screen_name`. This is not Twitter's canonical reply. Examples:: 

        @whatever @user blablabla -> True
        @user blablabla -> True
        bla @user blablabla -> False
    """
    return user_screen_name in tweet_replies(retweet['retweeted_status']['text'])

def retweet_mentions_user(retweet, user, is_screen_name=False):
    """
    Returns True if `retweet` mentions `user` using entities
    """
    format = 'screen_name' if is_screen_name else 'id'

    if 'retweeted_status' in retweet:
        for user_mentioned in retweet['retweeted_status']['entities']['user_mentions']:
            if user_mentioned[format] == user:
                return True
    return False 

def datetime_from_twitter_date(twitter_date):
    """
    Returns a datetime from a `twitter_date` string like "Mon Jul 14 18:16:57 +0000 2008"
    """
    return datetime.strptime(twitter_date, '%a %b %d %H:%M:%S +0000 %Y')

def deltatime_between_tweets(tweet1, tweet2):
    """
    Returns a deltatime between two tweets
    """
    return datetime_from_twitter_date(tweet2['created_at']) - datetime_from_twitter_date(tweet1['created_at'])

def retweets_by_user(user, is_screen_name=True, count=100):
    """
    Returns a JSON with `count` RTs from `user` 
    """
    format = 'screen_name' if is_screen_name else 'user_id'
   
    response = client.get('http://api.twitter.com/1/statuses/retweeted_by_user.json?%(format)s=%(user)s&count=%(count)s&include_entities=true'
        % {'format': format, 'user': user, 'count': count})

    if response.status_code == 200:
        remaining_calls = remaining_calls_from_response(response.headers)
        if remaining_calls <= 5:
            print "You have %s remaining calls left, be careful not reaching your limit, you could get black listed by Twitter" % remaining_calls
        return json.loads(response.content)
    else:
        raise TwitterAPIException(response)

def rts_by_user_with_automention(user, is_screen_name=True):
    """
    Returns a tuple containing:
        - Text of the RTs the `user` did mentioning himself
        - Deltatime between last RT and first
    """
    rts = retweets_by_user(user, is_screen_name)
    rts_automention = []

    for rt in rts:
        if retweet_mentions_user(rt, user, is_screen_name) and not retweet_replies_user(rt, user):
            rts_automention.append(rt['retweeted_status']['text'])
    
    if rts:
        return (rts_automention, deltatime_between_tweets(rts[len(rts)-1], rts[0]))
    else:
        raise TwitterException("Looks like the user doesn't have RTs, are you sure the user provided exists and is active?")


if __name__ == "__main__":
    # Parsing CLI
    parser = OptionParser()
    parser.add_option("-u", "--user", dest="user", help="Example: maraujop")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Verbose mode: print RTs texts")
    (options, args) = parser.parse_args()

    user = options.user
    if user is None:
        parser.error("You need to specify a user using option -u")

    # Setting up Open Authentication with requests using requests-oauth
    OAuthHook.consumer_key = TWITTER_CONSUMER_KEY
    OAuthHook.consumer_secret = TWITTER_CONSUMER_SECRET
    oauth_hook = OAuthHook(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    client = requests.session(hooks={'pre_request': oauth_hook})

    # Find the RTs a user did that were mentioning himself (ego)
    try:
        int(user)
        is_screen_name = False
    except ValueError:
        is_screen_name = True

    try:
         
        rts_and_delta = rts_by_user_with_automention(user, is_screen_name=is_screen_name)
    except (TwitterAPIException, TwitterException), e:
        print e.message
        sys.exit(1)

    delta = rts_and_delta[1]
    print "In the last 100 RTs by %s There were %s that mentioned him. That hapenned in %s days, %s hours, %s minutes" % (
        user, len(rts_and_delta[0]), delta.days, delta.seconds // 3600, delta.seconds // 60 % 60)

    # Print RTs if verbose mode is on
    if options.verbose:
        print '\n'
        for rt in rts_and_delta[0]:
            print "\t-> %s" % rt
