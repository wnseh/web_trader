#!/usr/bin/env python3

import sqlite3

connection = sqlite3.connect('master.db', check_same_thread = False)
cursor = connection.cursor()

query1 = '''CREATE TABLE doctor(
        doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR,
        balance VARCHAR
        );'''

query2 = '''CREATE TABLE patient(
        pat_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR,
        balance VARCHAR
        );'''
query3 = '''CREATE TABLE doc_pat(
        doc_id INTEGER FOREIGN KEY REFERENCES doctor(doc_id),
        pat_id INTEGER FOREIGN KEY REFERENCES patient(pat_id)
        );'''

cursor.execute(query1)
cursor.execute(query2)
cursor.execute(query3)

cursor.close()
connection.close()