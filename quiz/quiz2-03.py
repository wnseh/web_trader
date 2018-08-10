#!/usr/bin/env python3

import sqlite3

connection = sqlite3.connect('master.db', check_same_thread = False)
cursor = connection.cursor()

query1 = '''CREATE TABLE user(
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR,
        username VARCHAR(16),
        password VARCHAR(32),
        email TEXT
        );'''

query2 = '''CREATE TABLE admin(
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR,
        username VARCHAR(16),
        password VARCHAR(32),
        email TEXT
        );'''
query3 = '''CREATE TABLE user_phonenumber(
        number INTEGER PRIMARY KEY,
        pk FOREIGN KEY REFERENCES user(pk)
        );'''
query4 = '''CREATE TABLE admin_phonenumber(
        number INTEGER PRIMARY KEY,
        pk FOREIGN KEY REFERENCES admin(pk)
        );'''

cursor.execute(query1)
cursor.execute(query2)
cursor.execute(query3)
cursor.execute(query4)

cursor.close()
connection.close()