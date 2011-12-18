# Egometer

Egometer is a simple Python script released under the BSD license that measures the ego of a twitter user, based on the fact that the ego has some correlation with the number of retweets that person does in which is mentioned. It analyzes the last 100 RTs and tells you the time period between first and last RTs with automentions. Disclaimer it doesn't count replies retweeted, because I belive replies retweeted are usually not for ego boosting.

This is mainly a little experiment I did in a couple hours for playing with the Twitter API. This script uses <a href="https://github.com/kennethreitz/requests">requests</a> + <a href="https://github.com/maraujop/requests">requests-oauth</a>. Of course, this measure is not always reliable, but I've found that people with big egos tend to retweet things that talk about themselves to show off the world how cool they are. 

## Installation

There is no PyPi package for this, unless someone finds it interesting. So you can download or clone from Github:

    git clone git://github.com/maraujop/egometer.git
    cd egometer
    cp example_settings.py settings.py

Open `settings.py` with your favorite editor and feel in your Twitter API token information. `settings.py` is in .gitignore, so don't worry.

### Requirements

You need to install requests and requests-oauth in order to use this script. As easy as:

    pip install requests requests-oauth

## Usage

    $ python egometer -u maraujop
    In the last 100 RTs by maraujop There were 7 that mentioned him. That hapenned in 345 days, 3 hours, 8 minutes

* -u --user for specifying the user. You can pass a user screen name like `maraujop` or an id 
* -v --verbose for verbose use, this prints the text of the retweets with automentions

## Contributions

* There are many ways this script can be improved. Adding NLP processing or correlating this data with other aggregated data sources.
* If the script fails with a username or id without letting you know why, you can open a bug issue.
* Feel free to fork this repository and send contributions, fixes and enhancements.
