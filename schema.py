import sqlite3

connection = sqlite3.connect('trade_info.db',check_same_thread=False)
cursor = connection.cursor()

cursor.execute(
    """CREATE TABLE user(
        username TXT PRIMARY KEY,
        password VARCHAR,
        balance FLOAT
    );"""
)

cursor.execute(
    """CREATE TABLE transactions(
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker_symbol TEXT,
        num_shares FLOAT,
        owner_username VARCHAR,
        last_price FLOAT,
        FOREIGN KEY(owner_username) REFERENCES user(username)
    );"""
)

cursor.execute(
    """CREATE TABLE holdings(
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        last_price FLOAT,
        num_shares FLOAT,
        ticker_symbol VARCHAR(16),
        username VARCHAR,
        avg_price FLOAT,
        FOREIGN KEY (username) REFERENCES user(username)
    );"""
)

cursor.close()
connection.close()
