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

#Creating header for execution:
execution.write("Buy or sell | Price | Stoploss | Square off \n")

#%%
api_key = "uvWJebUEBC5MuZz0SWoyx9Il4HX9taXn59rpERsR"
api_secret = "d2kv2xvksl"
redirect_uri = "http://127.0.0.1"
s = Session(api_key)
s.set_redirect_uri(redirect_uri)
s.set_api_secret(api_secret)
print(s.get_login_url())
code = "52924422c089815ee2458fd8639a83770155c5f4"

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
    data = data.tail(100)
    data["sma5"] = data.cp.rolling(window=5).mean()
    data["sma50"] = data.cp.rolling(window=50).mean()
    return data

def buy(script, amount, stoploss, squareoff):
    cp = u.get_live_feed(u.get_instrument_by_symbol('NSE_EQ', script), LiveFeedType.LTP)
    return u.place_order(TransactionType.Buy,  # transaction_type
                 u.get_instrument_by_symbol('NSE_EQ', script),  # instrument
                 1,  # quantity
                 OrderType.Limit,  # order_type
                 ProductType.OneCancelsOther,  # product_type
                 cp['ltp'],  # price
                 None,  # trigger_price
                 0,  # disclosed_quantity
                 DurationType.DAY,  # duration
                 stoploss,  # stop_loss
                 squareoff,  # square_off
                 20)  # trailing_ticks 20 * 0.05

def sell(script, amount, stoploss, squareoff):
    cp = u.get_live_feed(u.get_instrument_by_symbol('NSE_EQ', script), LiveFeedType.LTP)
    return u.place_order(TransactionType.Sell,  # transaction_type
                 u.get_instrument_by_symbol('NSE_EQ', script),  # instrument
                 1,  # quantity
                 OrderType.Limit,  # order_type
                 ProductType.OneCancelsOther,  # product_type
                 cp['ltp'],  # price
                 None,  # trigger_price
                 0,  # disclosed_quantity
                 DurationType.DAY,  # duration
                 stoploss,  # stop_loss
                 squareoff,  # square_off
                 20)  # trailing_ticks 20 * 0.05

def SMACrossOver(ScriptData, script):
    if ScriptData.sma5.iloc[-6] < ScriptData.sma50.iloc[-6] and ScriptData.sma5.iloc[-5] < ScriptData.sma50.iloc[-5] and ScriptData.sma5.iloc[-4] < ScriptData.sma50.iloc[-4] and ScriptData.sma5.iloc[-3] < ScriptData.sma50.iloc[-3] and ScriptData.sma5.iloc[-2] > ScriptData.sma50.iloc[-2] and ScriptData.sma5.iloc[-1] > ScriptData.sma50.iloc[-1]:
        squareoff = float(round(abs(ScriptData.cp.iloc[-1] - (ScriptData.cp.iloc[-1] * 1.0075)), 0))
        stoploss = float(round(abs(ScriptData.cp.iloc[-1] - (ScriptData.cp.iloc[-1] * 1.01)), 0))
        buy(script, ScriptData.cp.iloc[-1], stoploss, squareoff)
        print("Buying at: %s -- stop loss at: %s --  square off at: %s" %(ScriptData.cp.iloc[-1], stoploss, squareoff))
        execution.write("Buy | %s | %s | %s \n" %(ScriptData.cp.iloc[-1], stoploss, squareoff))

    if ScriptData.sma5.iloc[-6] > ScriptData.sma50.iloc[-6] and ScriptData.sma5.iloc[-5] > ScriptData.sma50.iloc[-5] and ScriptData.sma5.iloc[-4] > ScriptData.sma50.iloc[-4] and ScriptData.sma5.iloc[-3] > ScriptData.sma50.iloc[-3] and ScriptData.sma5.iloc[-2] < ScriptData.sma50.iloc[-2] and ScriptData.sma5.iloc[-1] < ScriptData.sma50.iloc[-1]:
        squareoff = float(round(abs(ScriptData.cp.iloc[-1] - (ScriptData.cp.iloc[-1] * 1.0075)), 0))
        stoploss = float(round(abs(ScriptData.cp.iloc[-1] - (ScriptData.cp.iloc[-1] * 1.01)), 0))
        sell(script, ScriptData.cp.iloc[-1], stoploss, squareoff)
        print("Selling at: %s -- stop loss at: %s --  square off at: %s" %(ScriptData.cp.iloc[-1], stoploss, squareoff))
        execution.write("Sell | %s | %s | %s \n" %(ScriptData.cp.iloc[-1], stoploss, squareoff))    


#%%
def CheckTrades():
    now = datetime.now()
    now_time = now.time()

    if time(3,51) <= now_time <= time(8,45) and CheckBalance() > 1500:
        bucket = ["VAKRANGEE", "JINDALSTEL", "CANBK", "IBREALEST", "PCJEWELLER", "BANKINDIA", "ADANIENT", "FORTIS", "INFIBEAM", "RADICO", "RAIN", "DEEPAKNTR", "KPIT", "IGL", "GHCL", "DELTACORP", "STRTECH", "ASHOKA", "L&TFH", "EDELWEISS", "NBCC", "GSPL", "BOMDYEING", "EXIDEIND", "CASTROLIND", "HEXAWARE", "INDIANB", "JISLJALEQS", "EIHOTEL", "TATAGLOBAL"]

        for script in bucket:
            print("~~~~~~~~~~~~~~~~~~~~~~~ \n Now the time is: %s" % datetime.now().time())
            log.write("~~~~~~~~~~~~~~~~~~~~~~~ \n Now the time is: %s" % datetime.now().time())
            print("Checking for 50 min 5min MA Crossover for %s" % script)
            log.write("Checking for 50 min 5min MA Crossover for %s" % script)
            SMACrossOver(historicData(script, "22/03/2018", "23/03/2018"), script)

    elif time(9,28) <= now_time <= time(9,30):
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
    print("\n***Now waiting for 30 seconds")
    log.write("\n***Now waiting for 30 seconds")
    sleep.sleep(60)
