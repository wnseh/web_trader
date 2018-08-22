#!/usr/bin/env python3

from flask import Flask, render_template,request,session,redirect,jsonify
import json
import requests
import model
import sqlite3
import operator

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

@app.route('/terminal') #routes this
def menu():
#    if request.method == 'GET':
#        return render_template('index.html')
#    else:
#       submitted_username = request.form['username']
#       submitted_password = request.form['password']
#       print (submitted_username,submitted_password)
    return render_template('index.html')

@app.route('/terminal/register', methods=['GET','POST']) #tells you which methods are accepted
def create_account():
    if request.method =='GET':
        return render_template('create_account.html')
    else:
        submitted_username = request.form['username']
        submitted_password = request.form['password']
        submitted_balance = 10000 #hard coded for assessment request.form['balance']
        model.create(submitted_username,submitted_password,submitted_balance)
        return redirect('/terminal/login')

@app.route('/terminal/login',methods=['GET','POST'])
def login():
    if request.method =='POST':
        submitted_username = request.form['username']
        submitted_password = request.form['password']
        if model.log_in(submitted_username,submitted_password):
            session['username'] = submitted_username
            session['password'] = submitted_password
            if model.check_admin(submitted_username):
                session['isAdmin'] = True
            else:
                session['isAdmin'] = False
            return redirect('/terminal/mainmenu')
        else:
            return redirect('/terminal/login')
    return ''' 
	<form action = "/terminal/login" method='POST'>
		<p><input type = text name = username></p>
		<p><input type = text name = password></p>
		<p><input type = submit value = Login></p>
	</form>
	'''

@app.route('/terminal/mainmenu')
def main_menu():
    if session['isAdmin']:
        return render_template('main_menu.html')
    return render_template('main_menu.html')

@app.route('/terminal/quote', methods=['GET','POST'])
def quote():
    if request.method == 'GET':
        return render_template('quote.html')
    else:
        submitted_symbol = request.form['ticker_symbol']
        result = model.quote_last_price(submitted_symbol)
        return render_template('quote.html',
                               lastprice = result['LastPrice'], \
                               name = result['Name'],           \
                               volume = result['Volume'],       \
                               high = result['High'],           \
                               low = result['Low']
                              )

@app.route('/terminal/lookup', methods=['GET','POST'])
def lookup():
    if request.method == 'GET':
        return render_template('lookup.html')
    else:
        submitted_company_name = request.form['company_name']
        result = model.lookup_ticker_symbol(submitted_company_name)
        return render_template('lookup.html',result=result)

@app.route('/terminal/account')		
def check_balance():
    (balance,gains) = model.get_user_balance(session['username'])
    balance = "${0:.2f}".format(balance)
    gains = "${0:.2f}".format(gains)
    title = ''
    if session['isAdmin'] == False:
        title = 'Account'
        header = "Hi, {}. Here's your portfolio".format(session["username"])
        result = '''
        Your Gains/Loss(Theoretical): {gains}, Your Cash Balance: {balance}
        '''.format(gains = gains, balance=balance)
    else:
        title = 'LeaderBoard'
        model.updateHoldings()
        userlist = model.getUser()
        leaderboard = model.calculateLeaderBoard(userlist)
        header = 'Top 10 LeaderBoard'
        result = ''
        for x in range(len(leaderboard)):
            result += "Rank {}: Name: {} Gains: {}                |".format(x+1,leaderboard[x][0], leaderboard[x][1])
    return render_template('account.html',header=header,title=title, result=result, name = session['username'])

@app.route('/terminal/trade', methods=['GET','POST'])
def trade():
	if request.method == 'GET':
		return render_template('trade.html')
	else:
		submitted_ticker_symbol = request.form['ticker_symbol']
		submitted_trade_volume = request.form['trade_volume']
		submitted_order_type = request.form['order_type']
		if submitted_order_type == 'Buy':
			#calculate , display confirmation message with preview of trade, and execute if yes selected
			(confirmation, return_list) = model.buy(session['username'],submitted_ticker_symbol,submitted_trade_volume)
			if confirmation:
				model.buy_db(return_list)
			else:
				pass
				#User doesn't have enough balance
		else:
			#result = model.sell()
			(confirmation, return_list) = model.sell(session['username'],submitted_ticker_symbol,submitted_trade_volume)
			if confirmation:
				model.sell_db(return_list)
			else:
				pass
		return render_template('trade.html')

@app.route('/terminal/leaderboard', methods=['GET'])
def createleaderboard():
    userlist = model.getUser()
    return_list = model.calculateLeaderBoard(userlist) #list of tuples
    return_list.sort(reverse = True, key = operator.itemgetter(1))
    return_list = return_list[:10] #top 10
    return return_list

@app.route('/terminal/logout', methods=['GET'])
def logout():
    if session:
        session.clear()
    return redirect('/terminal')


app.run(debug=True)
