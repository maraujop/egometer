# -*- coding: utf-8 -*-

ERROR_CODES = {
    400: "Bad Request: The request was invalid. An accompanying error message will explain why. This is the status code will be returned during rate limiting.",
    401: "Unauthorized: Authentication credentials were missing or incorrect.",
    403: "Forbidden: The request is understood, but it has been refused. An accompanying error message will explain why. This code is used when requests are being denied due to update limits.",
    404: "Not Found: The URI requested is invalid or the resource requested, such as a user, does not exists.",
    406: "Not Acceptable: Returned by the Search API when an invalid format is specified in the request.",
    420: "Enhance Your Calm: Returned by the Search and Trends API when you are being rate limited.",
    500: "Internal Server Error: Something is broken. Please post to the group so the Twitter team can investigate.",
    502: "Bad Gateway: Twitter is down or being upgraded.",
    503: "Service Unavailable: The Twitter servers are up, but overloaded with requests. Try again later.",
}


class TwitterAPIException(Exception):
    def __init__(self, response):
        self.message = ERROR_CODES[response.status_code]

class TwitterException(Exception):
    def __init__(self, message):
        self.message = message
