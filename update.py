import tweepy
import re
import traceback
import datetime

from JST import JST
import db_service


class UpdateName():
    def __init__(self, auth, config):
        self.api = tweepy.API(auth)
        self._repatter = re.compile(config["updatename_regex"])
        self._rec_tweet = None
        # コンフィグデータの読み込み
        self._config = {
            "ng_words": config["ng_words"],
            "sabotage_words": config["sabotage_words"],
            "ng_users": config["ng_users"],
            "success_tweet": config["success_tweet"],
            "failure_tweet": config["failure_tweet"]
        }

    def check_friendship(self, target_screen_name):
        """
        target_screen_nameと相互フォローかどうかをチェック
        """
        source = self.api.me().screen_name
        # targetが自分なら常にTrue
        if(source == target_screen_name):
            return True
        result = self.api.show_friendship(
            source_screen_name=source, target_screen_name=target_screen_name)
        # resultは[0]に自分→相手のフォロー情報、[1]にその逆が入っている
        return result[1].following

    def extract_new_name(self, status):
        """
        新しい名前をstatusから抽出する
        """
        # 新しく設定する名前
        newname = status.text
        # 名前に適用できない文字を削除
        for n in ["\n", "\r", "\"", "\""]:
            newname = newname.replace(n, "")
        return newname

    def check_update(self, status):
        """
        名前をupdateするかどうかをチェックする
        """
        tweetstr = ""
        newname = self.extract_new_name(status)
        # ツイートしたユーザーのScreenName
        tweetuser_screenname = status.author.screen_name
        len(status.entities["hashtags"])
        # 長すぎ
        if len(newname) > 20:
            return False, None
        # ハッシュタグがある場合は反応しない
        elif len(status.entities["hashtags"]) > 0:
            return False, None
        # NGワードチェック
        for v in self._config["ng_words"]:
            if re.match(v, newname):
                tweetstr = "@%s %s" % (
                    tweetuser_screenname, self._config["failure_tweet"] % newname)
                return False, tweetstr
        # NGユーザーチェック
        for u in self._config["ng_users"]:
            if tweetuser_screenname == u:
                tweetstr = "@%s ﾀﾞﾒﾃﾞｰｽ" % (tweetuser_screenname)
                return False, tweetstr

        return True, None

    def update(self, status):

        # ツイートのID
        tweetid = status.id

        # ツイートしたユーザーのScreenName
        tweetuser_screenname = status.author.screen_name

        # ツイート本文
        tweetstr = ""
        check_result, fail_tweet = self.check_update(status)
        if check_result:
            newname = self.extract_new_name(status)
            try:
                # 名前が入っていれば名前変更の処理をする
                if newname:
                    # 動作時刻と変更前、後、変更したユーザー名を出力
                    last = datetime.datetime.now(tz=JST())
                    tstr = last.strftime("%y/%m/%d %H:%M:%S")
                    print("@%s: %s => %s (%s)" % (tweetuser_screenname,
                                                  self.api.me().name, newname, tstr))
                    db_service.insertUpdatelog(
                        status.author.screen_name, self.api.me().name, newname, tweetid)
                    self.api.update_profile(name=newname)
            except tweepy.error.TweepError as e:
                print(e.reason)
                tweetstr = "@%s 予期せぬエラーが発生したのでそういうのマジで勘弁して下さい @%s " % (
                    tweetuser_screenname, self.api.me().screen_name)
                # DM送っとく
                self.send_DM_to_self(self.create_error_message(
                    status, traceback.format_exc()))
                return status

        #　その人と相互フォローであれば投稿する
        if self.check_friendship(status.author.screen_name) and (tweetstr or fail_tweet):
            if fail_tweet:
                tweetstr = fail_tweet
            self._rec_tweet = self.api.update_status(
                status=tweetstr, in_reply_to_status_id=tweetid)

        return status

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
