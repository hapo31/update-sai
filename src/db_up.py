# -*- coding: utf-8 -*-

import sqlite3

import config

def main():
    # Update log DB
    try:
        conn = sqlite3.connect(config.log_db_name)
        create_table = '''
create table if not exists
    %s (
        id integer primary key autoincrement,
        date text,
        author text,
        from_name text,
        new_name text,
        url text
    )
''' % config.log_table

        conn.execute(create_table)
    except sqlite3.Error as e:
        print("failed create table(%s) %s" % (config.log_db_name, e.args[0]))

    # Error log DB
    try:
        conn = sqlite3.connect(config.error_db_name)
        create_table = '''
create table if not exists
    %s (
        id integer primary key autoincrement,
        date text,
        message text
    )
''' % config.error_table

        conn.execute(create_table)
    except sqlite3.Error as e:
        print("failed create table(%s) %s" % (config.error_db_name, e.args[0]))


    # Setting store DB
    try:
        # Reaction regexp word.
        conn = sqlite3.connect(config.setting_db_name)
        create_table = '''
create table if not exists
    %s (
        regexp text,
        success_tweet text,
        failure_tweet text
    )
''' % config.reaction_table

        conn.execute(create_table)
        conn.execute("insert into reaction (regexp, success_tweet, failure_tweet) values (?,?,?)", (config.updatename_regex, "我が名は%sである！", "我が名は%sではない！"))
        # NG users
        create_table = '''
create table if not exists
    %s (
        name text unique,
        enable int
    )
''' % config.ng_users_table

        conn.execute(create_table)
        # Add NG Users
        if len(config.ng_users) > 0:
            print("find NG User List(%d)" % len(config.ng_users))
            insert = '''
insert into %s (name, enable) values (?,?)
''' % config.ng_users_table

            users = [ (user, 1) for user in config.ng_words]
            conn.executemany(insert, users)
            conn.commit()

        # NG Words
        create_table = '''
create table if not exists
    %s (
        regexp text,
        enable int
    )
''' % config.ng_words_table

        conn.execute(create_table)
        # Add NG Word
        if len(config.ng_words) > 0:
            print("find NG Word List(%d)" % len(config.ng_words))
            insert = '''
insert into %s (regexp, enable) values (?,?)
''' % config.ng_words_table
            words = [ (word, 1) for word in config.ng_words]
            print(words)
            conn.executemany(insert, words)
            conn.commit()

        # Sabotage Words
        create_table = '''
create table if not exists
    %s (
        statement text,
        enable int
    )
''' % config.sabotage_words_table

        conn.execute(create_table)
        # Add sabotage words
        if len(config.sabotage_words) > 0:
            print("find Sabotage Word List(%d)" % len(config.sabotage_words))
            insert = '''
insert into %s (statement, enable) values (?,?)
''' % config.sabotage_words_table
            words = [ (word, 1) for word in config.sabotage_words]
            print(words)
            conn.executemany(insert, words)
            conn.commit()

    except sqlite3.Error as e:
        print("failed create table(%s) %s" % (config.setting_db_name, e.args[0]))


if __name__ == '__main__':
    main()

