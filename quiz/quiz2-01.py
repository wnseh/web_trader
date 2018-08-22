]#!/usr/bin/env python3

import sqlite3

connection = sqlite3.connect('master.db', check_same_thread = False)
cursor = connection.cursor()

query1 = '''CREATE TABLE state(
        state_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR,
        address VARCHAR
        );'''

query2 = '''CREATE TABLE city(
        city_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR,
        address VARCHAR,
        state_id INTEGER,
        FOREIGN KEY (state_id) REFERENCES state(state_id)
        );'''
query3 = '''CREATE TABLE park(
        park_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR,
        address VARCHAR,
        state_id INTEGER,
        FOREIGN KEY (state_id) REFERENCES state(state_id)
        );'''

cursor.execute(query1)
cursor.execute(query2)
cursor.execute(query3)


cursor.close()
connection.close()
