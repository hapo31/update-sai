#!/bin/python3
# -*- coding: utf-8 -*-

import traceback
import threading
from datetime import datetime
import sys

import tweepy
import db_service
import update


def init():
    import config
    auth = tweepy.OAuthHandler(
        consumer_key=config.consumer_key,
        consumer_secret=config.consumer_secret)
    auth.set_access_token(config.access_token, config.access_secret)

    return update.UpdateName(auth=auth, config=db_service.loadSettings())


def worker(updater, last_tweet=None):
    tweet_data = []
    changed = False
    target_status = None
    try:
        # if last_tweet is not None:
        #     # 以前取得したツイートから50秒以上経っていたら処理を続行
        #     delta = datetime.now() - last_tweet.created_at
        #     if delta.total_seconds() >= 50:
        #         last_tweet = None
        #     else:
        #         # 50秒以上経っていない場合は差の秒数分処理を先送りにする
        #         create_timer(60 - delta.total_seconds(),
        #                      last_tweet, updater, last_target_tweet)

        # since_idを取得して前回取得したツイート以降のツイートを取得する
        since_id = last_tweet.id if last_tweet is not None else None
        tweet_data = updater.api.home_timeline(since_id=since_id, count=200)

        for tweet in reversed(tweet_data):
            result, _ = updater.check_update(tweet)
            if result:
                target_status = tweet

        # 前回処理したツイートがNoneか、idが異なっていれば名前をupdateする
        if target_status:
            updater.update(target_status)
            changed = True

    except KeyboardInterrupt:
        sys.exit()
    except AttributeError:
        err = traceback.format_exc()
        print(err)
    except Exception as e:
        err = traceback.format_exc()
        print(err)
        # updater.send_DM_to_self(
        #     updater.create_error_message(None, err))
        # db_service.insertErrorLog(err)
    next_last_tweet = tweet_data[0] if len(tweet_data) > 0 else None
    create_timer(60, updater, next_last_tweet).start()


def create_timer(wait_seconds, updater, last_tweet):
    return threading.Timer(wait_seconds, worker, args=[updater, last_tweet])


if __name__ == "__main__":
    import os
    last_tweet = None

    print("Start Update_sai...")

    updater = init()

    threading.Thread(target=worker, args=(updater, None)).start()
