#!/bin/python3
# -*- coding: utf-8 -*-

import sqlite3

import config

# NGワードを取得する
def getNGWords():
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

# NGユーザーを取得する
def getNGUsers():
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

# サボり時反応ワードを取得する
def getSabotageWords():
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

# 基本設定を取得する
def getGeneralConfigs():
    conn = sqlite3.connect(config.setting_db_name)
    sql = "select * from %s limit 1" % config.reaction_table
    res_c = conn.execute(sql)
    res = {}
    for row in res_c:
        res["updatename_regex"] = row[0]
        res["success_tweet"] = row[1]
        res["failure_tweet"] = row[2]

    return res

def insertUpdatelog(author, fromName, newName, tweetId):
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
    res = getGeneralConfigs()
    ng_users = getNGUsers()
    ng_words = getNGWords()
    sabo_words = getSabotageWords()

    res["ng_users"] = ng_users
    res["ng_words"] = ng_words
    res["sabotage_words"] = sabo_words

    return res
