#!/bin/python3
# -*- coding: utf-8 -*-

import sqlite3

import config


def getNGWords():
    """
    NGワードを取得する
    """
    conn = sqlite3.connect(config.setting_db_name)
    sql = '''
select * from %s
''' % config.ng_words_table
    itr = conn.execute(sql)
    result = []
    for row in itr:
        if row[1] == 1:
            result.append(row[0])
    return result


def getNGUsers():
    """
    NGユーザーを取得する
    """
    conn = sqlite3.connect(config.setting_db_name)
    sql = '''
select * from %s
''' % config.ng_users_table
    itr = conn.execute(sql)
    result = []
    for row in itr:
        if row[1] == 1:
            result.append(row[0])
    return result


def getSabotageWords():
    """
    サボり時反応ワードを取得する
    """
    conn = sqlite3.connect(config.setting_db_name)
    sql = '''
select * from %s
''' % config.sabotage_words_table
    itr = conn.execute(sql)
    result = []
    for row in itr:
        if row[1] == 1:
            result.append(row[0])
    return result


def getGeneralConfigs():
    """
    基本設定を取得する
    """
    conn = sqlite3.connect(config.setting_db_name)
    sql = "select * from %s limit 1" % config.reaction_table
    res_c = conn.execute(sql)
    res = {}
    for row in res_c:
        res["updatename_regex"] = row[0]
        res["success_tweet"] = row[1]
        res["failure_tweet"] = row[2]

    return res


def getLastUpdateTweetId():
    """
    最後に反応したツイートのIDを取得する
    """
    conn = conn = sqlite3.connect(config.log_db_name)
    sql = "select url from %s order by date desc limit 1" % (config.log_table)

    res_cursor = conn.execute(sql)
    for row in res_cursor:
        return int(row[0])


def insertUpdatelog(author, fromName, newName, tweetId):
    """
    update時のログを挿入する
    """
    conn = sqlite3.connect(config.log_db_name)
    sql = '''
insert into %s (date, author, from_name, new_name, url)
values(
    datetime('now', 'localtime'),?,?,?,?
)
''' % config.log_table
    conn.execute(sql, (author, fromName, newName, tweetId))
    conn.commit()


def insertErrorLog(message):
    """
    エラーログを挿入する
    """
    conn = sqlite3.connect(config.error_db_name)
    sql = '''
insert into %s (date, message)
values(
    datetime('now', 'localtime'), ?
)
''' % config.error_table
    conn.execute(sql, (message,))
    conn.commit()


def loadSettings():
    """
    設定を読み込む
    """
    res = getGeneralConfigs()
    ng_users = getNGUsers()
    ng_words = getNGWords()
    sabo_words = getSabotageWords()

    res["ng_users"] = ng_users
    res["ng_words"] = ng_words
    res["sabotage_words"] = sabo_words

    return res
