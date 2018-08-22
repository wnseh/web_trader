#!/usr/bin/env

import json
import sqlite3
import requests
import operator

database = 'trade_info.db'

def check_admin(username):
    connection = sqlite3.connect(database, check_same_thread = False)
    cursor = connection.cursor()
    query = 'select isAdmin from user where username = "{}";'.format(username)
    cursor.execute(query)
    x = cursor.fetchone()
    if x[0] == 1:
        return True
    return False

def calculateHoldings(username):
    connection = sqlite3.connect(database, check_same_thread = False)
    cursor = connection.cursor()
    query = 'SELECT count(*), sum(num_shares*last_price) FROM holdings WHERE username = "{}";'.format(username)
    cursor.execute(query)
    x = cursor.fetchone()
    if x[0] != 0:
        return float(x[1])
    else:
        return 0
def calculateHistory(username):
    connection = sqlite3.connect(database, check_same_thread = False)
    cursor = connection.cursor()
    query = 'SELECT count(*), sum(num_shares* avg_price) FROM holdings WHERE username = "{}" ;'.format(username)
    cursor.execute(query)
    x = cursor.fetchone()
    if x[0] != 0: #if user has stock
        return float(x[1])
    else: 
        return 0
 #count total number of the shares that user currnetly holds
def calculate_user_gain(user):
    plus = calculateHoldings(user)
    minus = calculateHistory(user)
    gain = float(plus) - float(minus)
    return gain

def calculateLeaderBoard(userlist):
    connection = sqlite3.connect(database, check_same_thread=False)
    cursor = connection.cursor()
    list_ = []
    for user in userlist:
        gain = calculate_user_gain(user)
        x = (user, gain)
        list_.append(x)
    list_.sort(reverse =True, key = operator.itemgetter(1))
    list_ = list_[:10] #top 10
    return list_

def getUser():
    connection = sqlite3.connect(database, check_same_thread=False)
    cursor = connection.cursor()
    query = 'SELECT username FROM user;'
    cursor.execute(query)
    userlist =[row[0] for row in cursor.fetchall()]
    cursor.close()
    connection.close()
    return userlist

def log_in(user_name,password):
    connection = sqlite3.connect(database, check_same_thread=False)
    cursor = connection.cursor()
    query = 'SELECT count(*) FROM user WHERE username = "{}" AND password = "{}";'.format(user_name, password)
    cursor.execute(query)
    result_tuple = cursor.fetchone()
    if result_tuple[0] == 0:
        return False
    elif result_tuple[0] == 1:
        return True
    else:
        pass

def create(new_user,new_password,new_fund):
	connection = sqlite3.connect(database, check_same_thread=False)
	cursor = connection.cursor()
	isAdmin = 0
	cursor.execute(
		"""INSERT INTO user(
			username,
			password,
            isAdmin,
			balance
			) VALUES(
			'{}',
			'{}',
            {},
			{}
		);""".format(new_user,new_password,isAdmin,new_fund)
	)
	connection.commit()
	cursor.close()
	connection.close()

def display(username):
    connection = sqlite3.connect(database, check_same_thread=False)
    cursor = connection.cursor()
    query = '''SELECT count(*) FROM holdings WHERE username = "{}";'''.format(username)
    cursor.execute(query)
    havestock = cursor.fetchone()
    if havestock[0] == 0: #if user has no stock
        print("You don't own any stocks.")
    else:
        query2 = '''SELECT ticker_symbol, last_price, num_shares FROM holdings WHERE username = "{}";'''.format(username)
        cursor.execute(query2)
        stock_info = cursor.fetchall()
        for row in stock_info:
            print("Company: '{}', Stock Price: {}, Number of Shares: {}".format(row[0], row[1], row[2]))
    connection.close()

def updateHoldings():
    connection = sqlite3.connect(database, check_same_thread=False)
    cursor = connection.cursor()
    query = 'DELETE FROM holdings WHERE num_shares = 0'
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()
    
def sell(username, ticker_symbol, trade_volume):
	#we have to search for how many of the stock we have
	#compare trade volume with how much stock we have
	#if trade_volume <= our stock, proceed
	#else return to menu
	#we need a database to save how much money we have and how much stock
	trade_volume = float(trade_volume)
	connection = sqlite3.connect(database, check_same_thread=False)
	cursor = connection.cursor()
	query = 'SELECT count(*), num_shares FROM holdings WHERE username = "{}" AND ticker_symbol = "{}"'.format(username, ticker_symbol)
	cursor.execute(query)
	fetch_result = cursor.fetchone()
	if fetch_result[0] == 0:
		number_shares = 0
	else:
		current_number_shares = fetch_result[1]
	company_info = quote_last_price(ticker_symbol)
	last_price = float(company_info['LastPrice'])
	brokerage_fee = 6.95 #TODO un-hardcode this value
	(balance,gains) = get_user_balance(username) #TODO un-hardcode this value
	print("Price", last_price)
	print("brokerage fee", brokerage_fee)
	print("current balance", balance)
	transaction_revenue = (trade_volume * last_price) - brokerage_fee
	print("Total revenue of Transaction:", transaction_revenue)
	agg_balance = float(balance) + float(transaction_revenue)
	print("\nExpected user balance after transaction:", agg_balance)
	return_list = (last_price, brokerage_fee, balance, trade_volume,agg_balance,username,ticker_symbol, current_number_shares)
	if current_number_shares >= trade_volume:
		return True, return_list #success
	else:
		return False, return_list
		#if yes return new balance = current balance - transaction cost

def sell_db(return_list):
# return_list = (last_price, brokerage_fee, balance, trade_volume, agg_balance, username, ticker_symbol, current_number_shares)
    #check if user holds enough stock
    #update user's balance
    #insert transaction
    #if user sold all stocks holdings row should be deleted not set to 0
    connection = sqlite3.connect(database,check_same_thread = False)
    cursor = connection.cursor()
    last_price = return_list[0]
    brokerage_fee = return_list[1]
    balance = return_list[2]
    trade_volume = return_list[3]
    agg_balance = return_list[4]
    username = return_list[5]
    ticker_symbol = return_list[6]
    current_number_shares = return_list[7]

    #user
    cursor.execute("""
        UPDATE user
        SET balance = {}
        WHERE username = '{}'; 
    """.format(agg_balance, username)
    )
    #transactions
    cursor.execute("""
        INSERT INTO transactions(
        ticker_symbol,
        num_shares,
        owner_username,
        last_price
        ) VALUES(
        '{}',{},'{}',{}
        );""".format(ticker_symbol,trade_volume*-1,username,last_price)
    )
        #inserting information
    #holdings
    #at this point, it it assumed that the user has enough shares to sell.
    if current_number_shares >= trade_volume: #if user isn't selling all shares of a specific company
        tot_shares = float(current_number_shares)-float(trade_volume)
        cursor.execute('''
            UPDATE holdings
            SET num_shares = {}, last_price = {}
            WHERE username = "{}" AND ticker_symbol = "{}";
        '''.format(tot_shares, last_price, username, ticker_symbol)
        )
    connection.commit()
    cursor.close()
    connection.close()


def buy(username, ticker_symbol, trade_volume):
	#we need to return True or False for the confirmation message
	trade_volume = float(trade_volume)
	company_info = quote_last_price(ticker_symbol)
	last_price = float(company_info['LastPrice'])
	brokerage_fee = 6.95 #TODO un-hardcode this value
	(balance,gains) = get_user_balance(username) #TODO un-hardcode this value
	print("last price", last_price)
	print("brokerage fee", brokerage_fee)
	print("current balance", balance)
	transaction_cost = (trade_volume * last_price) + brokerage_fee
	print("Total cost of Transaction:", transaction_cost)
	left_over = float(balance) - float(transaction_cost)
	print("\nExpected user balance after transaction:", left_over)
	return_list = (last_price, brokerage_fee, balance, trade_volume,left_over,username,ticker_symbol)
	if transaction_cost <= balance:
		return True, return_list #success
	else:
		return False, return_list


def buy_db(return_list): # return_list = (last_price, brokerage_fee, balance, trade_volume, left_over, username, ticker_symbol)
    connection = sqlite3.connect(database,check_same_thread = False)
    cursor = connection.cursor()
    last_price = return_list[0]
    brokerage_fee = return_list[1]
    balance = return_list[2]
    trade_volume = return_list[3]
    left_over = return_list[4]
    username = return_list[5]
    ticker_symbol = return_list[6]

    #update users(balance), stocks, holdings.

    #users
        #updating the balance of the user
    cursor.execute("""
        UPDATE user
        SET balance = {}
        WHERE username = '{}'; 
    """.format(left_over, username)
    )
    #transactions
    cursor.execute("""
        INSERT INTO transactions(
        ticker_symbol,
        num_shares,
        owner_username,
        last_price
        ) VALUES(
        '{}',{},'{}',{}
        );""".format(ticker_symbol,trade_volume,username,last_price)
    )
    

        #inserting information
    #holdings
    query = 'SELECT count(*), num_shares, avg_price FROM holdings WHERE username = "{}" AND ticker_symbol = "{}"'.format(username, ticker_symbol)
    cursor.execute(query)
    fetch_result = cursor.fetchone()
    if fetch_result[0] == 0: #if the user didn't own the specific stock
        cursor.execute('''
            INSERT INTO holdings(last_price, num_shares, ticker_symbol, username, avg_price)
            VALUES (
            {},{},"{}","{}",{}
            );'''.format(last_price, trade_volume, ticker_symbol, username, last_price)
        )
    else: #if the user already has the same stock
        tot_shares = float(fetch_result[1])+float(trade_volume)
        calc_avg_price = (float(fetch_result[2])*float(fetch_result[1]) + trade_volume*last_price)/tot_shares
        cursor.execute('''
            UPDATE holdings
            SET num_shares = {}, last_price = {}, avg_price = {}
            WHERE username = "{}" AND ticker_symbol = "{}";
        '''.format(tot_shares, last_price, calc_avg_price, username, ticker_symbol)
        )
    connection.commit()
    cursor.close()
    connection.close()

def get_user_balance(username):
    connection = sqlite3.connect(database, check_same_thread = False)
    cursor = connection.cursor()
    query = 'SELECT balance FROM user WHERE username = "{}"'.format(username)
    cursor.execute(query)
    gains = calculate_user_gain(username)
    fetched_result = cursor.fetchone()
    cursor.close()
    connection.close()
    return fetched_result[0],gains #cursor.fetchone() returns tuples

def lookup_ticker_symbol(submitted_company_name):
    endpoint = 'http://dev.markitondemand.com/MODApis/Api/v2/Lookup/json?input='+submitted_company_name
    #FIXME The following return statement assumes that only one
    #ticker symbol will be matched with the user's input.
    #FIXME There also isn't any error handling.
    return json.loads(requests.get(endpoint).text)[0]['Symbol']


def quote_last_price(submitted_symbol):
    endpoint = 'http://dev.markitondemand.com/MODApis/Api/v2/Quote/json?symbol='+submitted_symbol
    stock_info = json.loads(requests.get(endpoint).text)
    return stock_info
    
    
    



'''
if __name__ == '__main__':
    userlist = ['jun', 'aileen', 'cen']
    print(calculateTransaction('jun', 'TSLA'))
'''
