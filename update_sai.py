#!/bin/python3
# -*- coding: utf-8 -*-

import traceback
import threading
from datetime import datetime
import sys

import tweepy
import db_service
import update

last_tweet = None


def init():
    import config
    auth = tweepy.OAuthHandler(
        consumer_key=config.consumer_key,
        consumer_secret=config.consumer_secret)
    auth.set_access_token(config.access_token, config.access_secret)

    return update.UpdateName(auth=auth, config=db_service.loadSettings())


def worker(updater, count=200):
    global last_tweet
    try:
        if last_tweet is not None:
            # 以前取得したツイートから90秒以上経っていたら消す
            delta = datetime.now() - last_tweet.created_at
            if delta.total_seconds() >= 90:
                last_tweet = None

        since_id = last_tweet.id if last_tweet is not None else None
        tweet_data = updater.api.home_timeline(since_id=since_id, count=count)

        print(tweet_data)

        status = None
        for tweet in reversed(tweet_data):
            result, _ = updater.check_update(tweet)
            if result:
                status = tweet

        if status:
            updater.update(status)

        # 取得したツイートの最新のものを保存しておく
        last_tweet = tweet_data[0]
    except KeyboardInterrupt:
        sys.exit()
    except AttributeError:
        err = traceback.format_exc()
        print(err)
    except Exception as e:
        err = traceback.format_exc()
        db_service.insertErrorLog(err)
        # updater.send_DM_to_self(
        #     updater.create_error_message(None, err))
        print(err)

    threading.Timer(60, worker, args=(updater))


if __name__ == "__main__":
    import os
    last_tweet = None

    print("Start Update_sai...")
    while True:
        updater = init()
        threading.Thread(target=worker, args=(updater, 200)).start()
