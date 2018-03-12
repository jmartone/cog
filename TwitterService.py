import tweepy
import time
import threading
import json
import functools
import types


class TwitterService:

    def __init__(self, credsFile, verbose = False, appAuth = False, jsonParser = True):
        if (verbose):
            print("Establishing connection")

        with open(credsFile, 'r') as creds:
            self.CREDS = json.loads(creds.read())

        self.limited = [False for _ in range(len(self.CREDS))]
        self.verbose = verbose
        self.appAuth = appAuth
        self.jsonParser = jsonParser
        self.cycle = 0
        self.updateConnection()

        def OOO():
            raise tweepy.TweepError()
        self.api.OOO = OOO

    def cycleLimit(self, limitedCycle):
        time.sleep(60*15+1)
        # reset the flag
        self.limited[limitedCycle] = False

    # legacy method, use self.api instead
    def getAPI(self):
        return self.api

    def updateConnection(self):
        self.twitterAuth = None
        if (self.appAuth):
            self.twitterAuth = tweepy.AppAuthHandler(self.CREDS[self.cycle]['CONSUMER_KEY'], self.CREDS[self.cycle]['CONSUMER_SECRET'])

        else:
            self.twitterAuth = tweepy.OAuthHandler(self.CREDS[self.cycle]['CONSUMER_KEY'], self.CREDS[self.cycle]['CONSUMER_SECRET'])
            self.twitterAuth.set_access_token(self.CREDS[self.cycle]['ACCESS_TOKEN'], self.CREDS[self.cycle]['ACCESS_TOKEN_SECRET'])
           
        if (self.jsonParser):
        	self.api = tweepy.API(self.twitterAuth, parser = tweepy.parsers.JSONParser())
        else:
        	self.api = tweepy.API(self.twitterAuth)

        if (self.verbose):
            print("Accessing the api as {}".format(self.CREDS[self.cycle]['NAME']))

    def hitLimit(self):
        if (self.verbose):
            print("Attempting to cycle authentication")

        # flag the current cycle as limited
        self.limited[self.cycle] = True

        # begin a countdown thread to refresh
        thread = threading.Thread(target = self.cycleLimit, args = (self.cycle,))
        thread.setDaemon(True)
        thread.start()

        self.cycleAuth()

    # def limit_wrapper(self, method):
    #     @functools.wraps(method)
    #     def wrapper(*args, **kwargs): # Note: args[0] points to 'self'.
    #         while True:
    #             try:
    #                 return method(*args, **kwargs)
    #                 break
    #             except tweepy.TweepError as e:
    #                 if hasattr(e, 'response') and hasattr(e.response, 'status_code') and e.response.status_code == 429:
    #                     self.hitLimit()
    #                 else:
    #                     raise e
    #     return wrapper

    # pass valid API calls to self.api
    def __getattr__(self, name, *args, **kwargs):
        if hasattr(self.api, name):
            attr = getattr(self.api, name)
            if callable(attr):
                # wrap it up!
                return attr
                # return self.limit_wrapper(attr)
            else:
                return attr
        else:
            super(TwitterService, self).__getattr__(name, value)

    def cycleAuth(self):
        if all(self.limited):
            print("Waiting for an authentication to open")
            while all(self.limited):
                pass
                time.sleep(1)
                
        for c, limit in enumerate(self.limited):
            if (not limit):
                self.cycle = c
                break

        self.updateConnection()
        if (self.verbose):
            print("Authentication cycled")
            print("{} cycle(s) remaining".format(self.limited.count(False)))