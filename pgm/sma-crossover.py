#Importing packages
from upstox_api import *
import datetime
import os
import pandas as pd
from matplotlib import pyplot as plt

#Writing codes to log into the api
api_key = "<YOUR API KEY>"
api_secret = "<YOUR API SECRET>"
redirect_uri = "<YOUR REDIRECT URI>"
s = Session(api_key)
s.set_redirect_uri(redirect_uri)
s.set_api_secret(api_secret)
print(s.get_login_url())
code = input("What is the code that you obtained from the URL?")

s.set_code (code)
access_token = s.retrieve_access_token()

u = Upstox ('api_key', access_token)

print("Login successful. Verify profile:")
print(u.get_profile())

master = u.get_master_contract('NSE_EQ')  # get contracts for NSE EQ

#function to fetch historic data
def historicData(script, start_dt, end_dt):
    data = pd.DataFrame(u.get_ohlc(u.get_instrument_by_symbol('NSE_EQ', script),
                      OHLCInterval.Minute_1,
                      datetime.datetime.strptime(start_dt, '%d/%m/%Y').date(),
                      datetime.datetime.strptime(end_dt, '%d/%m/%Y').date()))
    data.head()
    data["sma5"] = data.cp.rolling(window=5).mean()
    data["sma50"] = data.cp.rolling(window=50).mean()
    return data

def buy(script, amount, stoploss, squareoff):
    return u.place_order(TransactionType.Buy,  # transaction_type
                 u.get_instrument_by_symbol('NSE_EQ', script),  # instrument
                 5,  # quantity
                 OrderType.Limit,  # order_type
                 ProductType.OneCancelsOther,  # product_type
                 amount,  # price
                 None,  # trigger_price
                 0,  # disclosed_quantity
                 DurationType.DAY,  # duration
                 stoploss,  # stop_loss
                 squareoff,  # square_off
                 20)  # trailing_ticks 20 * 0.05

def sell(script, amount, stoploss, squareoff):
    return u.place_order(TransactionType.Sell,  # transaction_type
                 u.get_instrument_by_symbol('NSE_EQ', script),  # instrument
                 5,  # quantity
                 OrderType.Limit,  # order_type
                 ProductType.OneCancelsOther,  # product_type
                 amount,  # price
                 None,  # trigger_price
                 0,  # disclosed_quantity
                 DurationType.DAY,  # duration
                 stoploss,  # stop_loss
                 squareoff,  # square_off
                 20)  # trailing_ticks 20 * 0.05

def SMACrossOver(ScriptData):
    if ScriptData.sma5.iloc[-6] < ScriptData.sma50.iloc[-6] and ScriptData.sma5.iloc[-5] < ScriptData.sma50.iloc[-5] and ScriptData.sma5.iloc[-4] < ScriptData.sma50.iloc[-4] and ScriptData.sma5.iloc[-3] < ScriptData.sma50.iloc[-3] and ScriptData.sma5.iloc[-2] > ScriptData.sma50.iloc[-2] and ScriptData.sma5.iloc[-1] > ScriptData.sma50.iloc[-1]:
        squareoff = float(round(abs(ScriptData.cp.iloc[-1] - ScriptData.high.iloc[-1] * 1.01), 0))
        stoploss = float(round(abs(ScriptData.cp.iloc[-1] - ScriptData.low.iloc[-1] * 0.99), 0))
        print("Buying at: %s -- stop loss at: %s --  square off at: %s" %(ScriptData.cp.iloc[-1], stoploss, squareoff))
        buy(script, ScriptData.cp.iloc[-1], stoploss, squareoff)
        
    if ScriptData.sma5.iloc[-6] > ScriptData.sma50.iloc[-6] and ScriptData.sma5.iloc[-5] > ScriptData.sma50.iloc[-5] and ScriptData.sma5.iloc[-4] > ScriptData.sma50.iloc[-4] and ScriptData.sma5.iloc[-3] > ScriptData.sma50.iloc[-3] and ScriptData.sma5.iloc[-2] < ScriptData.sma50.iloc[-2] and ScriptData.sma5.iloc[-1] < ScriptData.sma50.iloc[-1]:
        stoploss = float(round(abs(ScriptData.cp.iloc[-1] - ScriptData.high.iloc[-1] * 1.01), 0))
        squareoff = float(round(abs(ScriptData.cp.iloc[-1] - ScriptData.low.iloc[-1] * 0.99), 0))
        print("Selling at: %s -- stop loss at: %s --  square off at: %s" %(ScriptData.cp.iloc[-1], stoploss, squareoff))
        sell(script, ScriptData.cp.iloc[-1], stoploss, squareoff)

bucket = ["ADANIENT","APOLLOTYRE","AXISBANK","BHARTIARTL","BIOCON","BOMDYEING","BPL","CANBK","DISHTV","EXIDEIND","FEDERALBNK","FORTIS",
            "HBLPOWER","HDIL","HINDCOPPER","HUDCO","ICICIBANK","IDFC","IDFCBANK","INDIACEM","INFIBEAM","IRB","JAMNAAUTO","JETAIRWAYS",
            "JINDALSTEL","JSWENERGY","KEC","KPIT","KRIDHANINF","KWALITY","L&TFH","MANAPPURAM","MOTHERSUMI","NATIONALUM","ORIENTBANK",
            "PCJEWELLER","PNB","RECLTD","RELCAPITAL","RELIANCE","SBIN","SETCO","SPTL","SYNDIBANK","TATAGLOBAL","TATAMOTORS","TITAN",
            "TV18BRDCST","UNIONBANK","VEDL"]

for script in bucket:
    print("~~~~~~~~~~~~~~~~~~~~~~~ \n Now the time is: %s" %datetime.datetime.now().time())
    print("Checking for 50 min 5min MA Crossover for %s" % script)
    SMACrossOver(historicData(script, "22/12/2017", "22/12/2017"))
