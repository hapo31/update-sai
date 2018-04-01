#!/bin/python3
# -*- coding: utf-8 -*-

import re
import datetime
import random
import traceback
import tweepy

import db_service


class MyStreamListener(tweepy.StreamListener):
    """
    tweepyのStreamListenerを実装するクラス
    """

    def __init__(self, auth, config):
        super(MyStreamListener, self).__init__(api=tweepy.API(auth))
        self._repatter = re.compile(config["updatename_regex"])
        self._rec_tweet = None
        self._user_history = {"": UsesCount()}
        self._me_screenname = self.api.me().screen_name
        # コンフィグデータの読み込み
        self._config = {
            "ng_words": config["ng_words"],
            "sabotage_words": config["sabotage_words"],
            "ng_users": config["ng_users"],
            "success_tweet": config["success_tweet"],
            "failure_tweet": config["failure_tweet"]
        }

        # try:
        #     #self.api.update_status(status=("@%s update_saiを起動しました。" % me_screenname) )
        #     pass
        # except tweepy.error.TweepError as e:
        #     pass
        # write_log("Start process.")

    # target_screen_nameと相互フォローかどうかをチェック
    def check_friendship(self, target_screen_name):
        source = self.api.me().screen_name
        # targetが自分なら常にTrue
        if(source == target_screen_name):
            return True
        result = self.api.show_friendship(
            source_screen_name=source, target_screen_name=target_screen_name)
        # resultは[0]に自分→相手のフォロー情報、[1]にその逆が入っている
        return result[1].following

    def on_status(self, status):
        allusers = "#allusers"

        # 新しく設定する名前
        newname = status.text
        # 名前に適用できない文字を削除
        for n in ["\n", "\r", "\"", "\""]:
            newname = newname.replace(n, "")

        if(self._repatter.match(newname)):
            try:
                if(self._rec_tweet.id == status.id):
                    return True
            except AttributeError:
                pass

            # ツイートのID
            tweetid = status.id

            # ツイートしたユーザーのScreenName
            tweetuser_screenname = status.author.screen_name

            # ツイート本文
            tweetstr = ""
            len(status.entities["hashtags"])
            # 長すぎ
            if len(newname) > 20:
                newname = ""
                tweetstr = ""
            # ハッシュタグがある場合は反応しない
            elif len(status.entities["hashtags"]) > 0:
                newname = ""
                tweetstr = ""
            # ユーザー全体の使用履歴の確認
            elif allusers in self._user_history and not self._user_history[allusers].Use(10):
                # 過去20分で10回以上使われていたらランダムにつぶやいてupdate nameしない
                i = random.randrange(len(self._config["sabotage_words"]))
                tweetstr = "@%s %s" % (
                    tweetuser_screenname, self._config["sabotage_words"][i])
                newname = ""
            # 個人の使用履歴の確認
            elif tweetuser_screenname in self._user_history and not self._user_history[tweetuser_screenname].Use():
                # 使いすぎマンにはおしおき
                tweetstr = "@%s 使いすぎじゃボケ" % (tweetuser_screenname)
                newname = ""
                # write_log("@%s use count:%d" % (tweetuser_screenname, self._user_history[tweetuser_screenname].use_count))
            # 正常処理
            else:
                # 使用者が使用履歴にまだいない場合は追加
                if tweetuser_screenname not in self._user_history:
                    self._user_history[tweetuser_screenname] = UsesCount()
                # write_log("@%s use count:%d" % (tweetuser_screenname, self._user_history[tweetuser_screenname].use_count))

                # newname = newname[::-1]
                # 成功時のツイート本文
                tweetstr = "@%s %s" % (
                    tweetuser_screenname, self._config["success_tweet"] % newname)
                if allusers not in self._user_history:
                    self._user_history[allusers] = UsesCount()
                # write_log("all user use count: %d" % self._user_history[allusers].use_count)
            # NGワードチェック
            for v in self._config["ng_words"]:
                if re.match(v, newname):
                    tweetstr = "@%s %s" % (
                        tweetuser_screenname, self._config["failure_tweet"] % newname)
                    newname = ""
                    break
            for u in self._config["ng_users"]:
                if tweetuser_screenname == u:
                    tweetstr = "@%s ちんぽ(ﾎﾞﾛﾝｯ)" % (tweetuser_screenname)
                    newname = ""
                    break
            try:
                # 名前が入っていれば名前変更の処理をする
                if newname:

                    # 動作時刻と変更前、後、変更したユーザー名を出力
                    last = self._user_history[tweetuser_screenname].last_time
                    tstr = last.strftime("%y/%m/%d %H:%M:%S")
                    print("@%s: %s => %s (%s)" % (tweetuser_screenname,
                                                  self.api.me().name, newname, tstr))
                    db_service.insertUpdatelog(
                        status.author.screen_name, self.api.me().name, newname, tweetid)
                    self.api.update_profile(name=newname)
            except tweepy.error.TweepError as e:
                print(e.reason)
                # write_log("Exception raised:%s " % e.reason)
                tweetstr = "@%s 予期せぬエラーが発生したのでそういうのマジで勘弁して下さい @%s " % (
                    tweetuser_screenname, self.api.me().screen_name)
                # DM送っとく
                self.send_DM_to_self(self.create_error_message(
                    status, traceback.format_exc()))
                return True
            finally:
                #　その人と相互フォローであれば投稿する
                if(self.check_friendship(status.author.screen_name) and tweetstr):
                    self._rec_tweet = self.api.update_status(
                        status=tweetstr, in_reply_to_status_id=tweetid)
                    # write_log("Tweeted:%s" % tweetstr)

        return True

    def on_error(self, status):
        # write_log("on_error:%s" % status)
        print(status)

    def create_error_message(self, status, stacktrace_text):
        return """
==== update-sai error report ====
date: %s
url: %s
tweet: %s
stack_trace:
%s
==== end error report ====
        """ % (
            str(datetime.datetime.now(tz=JST())),
            "https://twitter.com/%s/status/%s" % (
                status.author.screen_name, status.id) if status else "<runtime error>",
            status.text if status else "<runtime error>",
            stacktrace_text
        )

    def send_DM_to_self(self, text):
        self.api.send_direct_message(
            screen_name=self.api.me().screen_name, text=text)


class UsesCount(object):

    default_max_use_count = 3
    max_minutes = 20

    def __init__(self):
        self._first_time = datetime.datetime.now(tz=JST())
        self._last_time = datetime.datetime.now(tz=JST())
        self._use_count = 1

    def Use(self, count=0):
        # countが指定されていない場合はdefault_max_use_count回
        count = UsesCount.default_max_use_count if count == 0 else count
        self._use_count += 1
        self._last_time = datetime.datetime.now(tz=JST())
        # max_minutes分以内のcount回以上の使用を禁ずる
        if (self._last_time - self._first_time).seconds <= UsesCount.max_minutes * 60:
            if self._use_count > count:
                return False
        else:
            self._first_time = datetime.datetime.now(tz=JST())
            self._use_count = 1

        # write_log("use count:%d" % self._use_count)
        return True

    @property
    def first_time(self):
        return self._first_time

    @property
    def last_time(self):
        return self._last_time

    @property
    def use_count(self):
        return self._use_count

    def Reset(self):
        self.__init__()


class JST(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(hours=9)

    def dst(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return "JST"


def init():
    import config
    auth = tweepy.OAuthHandler(
        consumer_key=config.consumer_key,
        consumer_secret=config.consumer_secret)
    auth.set_access_token(config.access_token, config.access_secret)

    mystream = MyStreamListener(auth=auth, config=db_service.loadSettings())
    return auth, tweepy.Stream(auth=auth, listener=mystream), mystream


if __name__ == "__main__":
    import os
    import sys

    print("Start Update_sai...")
    while True:
        auth, stream, streamClass = init()
        try:
            stream.userstream()
        except KeyboardInterrupt as e:
            sys.exit()
        except AttributeError as e:
            pass
        except Exception as e:
            err = traceback.format_exc()
            db_service.insertErrorLog(err)
            streamClass.send_DM_to_self(
                streamClass.create_error_message(None, err))
            print(err)
