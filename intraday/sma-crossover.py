# -*- coding: utf-8 -*-
"""
Created on Sun Mar 18 10:29:35 2018

@author: Gireesh Sundaram
"""

#Importing packages
from upstox_api.api import *
from datetime import datetime, time
import time as sleep
import os
import pandas as pd

#%%
#Opening two TXT files here to write log
log = open("D:\\Upstox\\log\\log.txt", "w")
execution = open("D:\\Upstox\\log\\execution.txt", "w")

quantity = 3

#Creating header for execution:
execution.write("Script | Buy or sell | Price | Stoploss | Square off \n")

#%%
api_key = "api_key"
api_secret = "api_secret"
redirect_uri = "http://127.0.0.1"
s = Session(api_key)
s.set_redirect_uri(redirect_uri)
s.set_api_secret(api_secret)
print(s.get_login_url())
code = "Code"

s.set_code (code)
access_token = s.retrieve_access_token()

u = Upstox (api_key, access_token)

print("Login successful. Verify profile:")
log.write("\nLogin successful. Verify profile:")
print(u.get_profile())
log.write("\n" % u.get_profile())

#%%
master = u.get_master_contract('NSE_EQ')  # get contracts for NSE EQ

#Function to fetch the current available balance:
def CheckBalance():
    balance = pd.DataFrame(u.get_balance())
    balance1 = balance["equity"]["available_margin"]
    return balance1

#function to fetch historic data
def historicData(script, start_dt, end_dt):
    data = pd.DataFrame(u.get_ohlc(u.get_instrument_by_symbol('NSE_EQ', script),
                      OHLCInterval.Minute_1,
                      datetime.strptime(start_dt, '%d/%m/%Y').date(),
                      datetime.strptime(end_dt, '%d/%m/%Y').date()))
    data = data.tail(60)
    data["sma5"] = data.cp.rolling(window=5).mean()
    data["sma50"] = data.cp.rolling(window=50).mean()
    data["difference"] =  data["sma5"] -  data["sma50"]
    print(data.tail(5))
    return data

def IsLoss(stock):
    position = pd.DataFrame(u.get_positions())
    if position.empty:
        return True
    realized = position.loc[position["realized_profit"] < -6]["symbol"].tolist()
    if stock not in realized or not realized:
        return True
    elif stock in realized:
        print("We have already took loss in %s not buying again" %stock)
        log.write("We have already took loss in %s not buying again" %stock)
        return False

def CheckPositionSell(stock):
    position = pd.DataFrame(u.get_positions())
    if position.empty:
        return True
    bought = position.loc[position["net_quantity"] > 0]["symbol"].tolist()
    if stock not in bought or not bought:
        return True
    elif stock in bought:
        print("There is already a long position on %s, so not selling" %stock)
        log.write("There is already a long position on %s, so not selling" %stock)
        return False

def CheckPositionBuy(stock):
    position = pd.DataFrame(u.get_positions())
    if position.empty:
        return True
    sold = position.loc[position["net_quantity"] < 0]["symbol"].tolist()
    if stock not in sold or not sold:
        return True
    elif stock in sold:
        print("There is already a short position on %s, so not buying" %stock)
        log.write("There is already a short position on %s, so not buying" %stock)
        return False

def buy(script):
    cp = u.get_live_feed(u.get_instrument_by_symbol('NSE_EQ', script), LiveFeedType.LTP)
    price = float(cp['ltp'])
    squareoff = abs(round(cp["ltp"] * 1/100, 0))
    stoploss = abs(round(cp["ltp"] * 0.75/100, 0))
    print("Buying at: %s -- stop loss at: %s --  square off at: %s" %(cp['ltp'], stoploss, squareoff))
    execution.write("%s | Buy | %s | %s | %s \n" %(script, cp['ltp'], stoploss, squareoff))

    return u.place_order(TransactionType.Buy,  # transaction_type
                 u.get_instrument_by_symbol('NSE_EQ', script),  # instrument
                 quantity,  # quantity
                 OrderType.Limit,  # order_type
                 ProductType.OneCancelsOther,  # product_type
                 price,  # price
                 None,  # trigger_price
                 0,  # disclosed_quantity
                 DurationType.DAY,  # duration
                 stoploss,  # stop_loss
                 squareoff,  # square_off
                 20)  # trailing_ticks 20 * 0.05

def sell(script):
    cp = u.get_live_feed(u.get_instrument_by_symbol('NSE_EQ', script), LiveFeedType.LTP)
    price = float(cp['ltp'])
    squareoff = abs(round(cp["ltp"] * 1/100, 0))
    stoploss = abs(round(cp["ltp"] * 0.75/100, 0))
    print("Selling at: %s -- stop loss at: %s --  square off at: %s" %(cp['ltp'], stoploss, squareoff))
    execution.write("%s | Sell | %s | %s | %s \n" %(script, cp['ltp'], stoploss, squareoff))    
    

    return u.place_order(TransactionType.Sell,  # transaction_type
                 u.get_instrument_by_symbol('NSE_EQ', script),  # instrument
                 quantity,  # quantity
                 OrderType.Limit,  # order_type
                 ProductType.OneCancelsOther,  # product_type
                 price,  # price
                 None,  # trigger_price
                 0,  # disclosed_quantity
                 DurationType.DAY,  # duration
                 stoploss,  # stop_loss
                 squareoff,  # square_off
                 20)  # trailing_ticks 20 * 0.05

def SMACrossOver1(ScriptData, script):
    if ScriptData.sma5.iloc[-6] < ScriptData.sma50.iloc[-6] and ScriptData.sma5.iloc[-5] < ScriptData.sma50.iloc[-5] and ScriptData.sma5.iloc[-4] < ScriptData.sma50.iloc[-4] and ScriptData.sma5.iloc[-3] < ScriptData.sma50.iloc[-3] and ScriptData.sma5.iloc[-2] > ScriptData.sma50.iloc[-2] and ScriptData.sma5.iloc[-1] > ScriptData.sma50.iloc[-1]:
        if CheckPositionBuy(script) and IsLoss(script):
            buy(script)

    if ScriptData.sma5.iloc[-6] > ScriptData.sma50.iloc[-6] and ScriptData.sma5.iloc[-5] > ScriptData.sma50.iloc[-5] and ScriptData.sma5.iloc[-4] > ScriptData.sma50.iloc[-4] and ScriptData.sma5.iloc[-3] > ScriptData.sma50.iloc[-3] and ScriptData.sma5.iloc[-2] < ScriptData.sma50.iloc[-2] and ScriptData.sma5.iloc[-1] < ScriptData.sma50.iloc[-1]:
        if CheckPositionSell(script) and IsLoss(script):
            sell(script)
            
def SMACrossOver2(ScriptData, script):
    if ScriptData.difference.iloc[-6] < 0 and ScriptData.difference.iloc[-5] < 0 and ScriptData.difference.iloc[-4] < 0 and ScriptData.difference.iloc[-3] < 0 and ScriptData.difference.iloc[-2] < 0 and ScriptData.difference.iloc[-1] < 0 and (ScriptData.difference.iloc[-6] < ScriptData.difference.iloc[-5] < ScriptData.difference.iloc[-4] < ScriptData.difference.iloc[-3] < ScriptData.difference.iloc[-2] < ScriptData.difference.iloc[-1]) and -0.2 <= ScriptData.difference.iloc[-1] <= 0:
        if CheckPositionBuy(script) and IsLoss(script):
            buy(script)

    if ScriptData.difference.iloc[-6] > 0 and ScriptData.difference.iloc[-5] > 0 and ScriptData.difference.iloc[-4] > 0 and ScriptData.difference.iloc[-3] > 0 and ScriptData.difference.iloc[-2] > 0 and ScriptData.difference.iloc[-1] > 0 and (ScriptData.difference.iloc[-6] > ScriptData.difference.iloc[-5] > ScriptData.difference.iloc[-4] > ScriptData.difference.iloc[-3] > ScriptData.difference.iloc[-2] > ScriptData.difference.iloc[-1]) and 0 <= ScriptData.difference.iloc[-1] <= 0.2:
        if CheckPositionSell(script) and IsLoss(script):
            sell(script)
           
#%%
def CheckTrades():
    now = datetime.now()
    now_time = now.time()

    if time(10,21) <= now_time <= time(14,15) and CheckBalance() > 500:
        bucket1 = ["ABAN", "APOLLOTYRE", "BEPL", "CANBK", "DATAMATICS", "FORTIS", "IBREALEST", "INDIACEM", "IRB", "JINDALSTEL", "KPIT", "NBCC", "PCJEWELLER", "SANGHIIND", "TAKE"]
        bucket2 = ["ADANIENT", "BANKINDIA", "BOMDYEING", "CROMPTON", "DELTACORP", "HINDOILEXP", "IBVENTURES", "INFIBEAM", "JAICORPLTD", "JISLJALEQS", "KTKBANK", "NCC", "PRAKASH", "SUVEN", "TATAGLOBAL"]

        for script in bucket1:
            print("~~~~~~~~~~~~~~~~~~~~~~~ \n Now the time is: %s" % datetime.now().time())
            log.write("~~~~~~~~~~~~~~~~~~~~~~~ \n Now the time is: %s" % datetime.now().time())
            print("Checking for 50 min 5min MA Crossover for %s" % script)
            log.write("Checking for 50 min 5min MA Crossover for %s" % script)
            SMACrossOver1(historicData(script, "08/04/2018", "09/04/2018"), script)
            
        for script2 in bucket2:
            print("~~~~~~~~~~~~~~~~~~~~~~~ \n Now the time is: %s" % datetime.now().time())
            log.write("~~~~~~~~~~~~~~~~~~~~~~~ \n Now the time is: %s" % datetime.now().time())
            print("Checking for 50 min 5min MA Crossover for %s" % script2)
            log.write("Checking for 50 min 5min MA Crossover for %s" % script2)
            SMACrossOver2(historicData(script2, "10/04/2018", "10/04/2018"), script2)

    elif time(14,58) <= now_time <= time(15,00):
        print("Exiting all the open position now and exiting execution")
        log.write("Exiting all the open position now and exiting execution")
        u.cancel_all_orders() #Cancel all open orders
        log.close()
        execution.close()
        exit()

    else:
        print("There is no market activity now. Checking in 2 mins.. Now the time is: %s" % datetime.now().time())
        log.write("There is no market activity now. Checking in 2 mins.. Now the time is: %s" % datetime.now().time())
        sleep.sleep(120)

#%%
while True:
    CheckTrades()
    print("\n***Now waiting for 60 seconds")
    log.write("\n***Now waiting for 60 seconds")
    sleep.sleep(60)
