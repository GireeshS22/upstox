#importing necessary packages
from upstox_api.api import *
import datetime

#Getting access tokens and logging in:
api_key = "<YOUR API KEY>"
api_secret = "<YOUR API SECRET>"
s = Session (api_key)
s.set_redirect_uri ('<YOUR REDIRECT URI>')
s.set_api_secret (api_secret)

print (s.get_login_url())
code = input("What is the code that you obtained from the URL?")

s.set_code (code)
access_token = s.retrieve_access_token()

u = Upstox (api_key, access_token)

print("Login successful. Verify profile:")
print(u.get_profile())

master = u.get_master_contract('NSE_EQ')  # get contracts for NSE EQ

#########################################################################
#function to fetch historic data
def historicData(script, start_dt, end_dt):
    data = u.get_ohlc(u.get_instrument_by_symbol('NSE_EQ', script),
                      OHLCInterval.Minute_1,
                      datetime.datetime.strptime(start_dt, '%d/%m/%Y').date(),
                      datetime.datetime.strptime(end_dt, '%d/%m/%Y').date())
    return data

#defining 5 minute moving average for the last 5 mins from historic data
def movingAve5m(script):
    temp = historicData(script, datetime.datetime.now().strftime("%d/%m/%Y"), datetime.datetime.now().strftime("%d/%m/%Y"))
    average = (temp[-1]["cp"] + temp[-2]["cp"] + temp[-3]["cp"] + temp[-4]["cp"] + temp[-5]["cp"]) / 5
    # rounding to nearest 0.05 precision
    averageRound = round(0.05 * round(float(average) / 0.05), 2)
    return averageRound

def movingAve10m(script):
    temp = historicData(script, datetime.datetime.now().strftime("%d/%m/%Y"), datetime.datetime.now().strftime("%d/%m/%Y"))
    average = (temp[-1]["cp"] + temp[-2]["cp"] + temp[-3]["cp"] + temp[-4]["cp"] + temp[-5]["cp"] + temp[-6]["cp"] + temp[-7]["cp"] + temp[-8]["cp"] + temp[-9]["cp"] + temp[-10]["cp"]) / 10
    # rounding to nearest 0.05 precision
    averageRound = round(0.05 * round(float(average) / 0.05), 2)
    return averageRound

def buy(symbol):
    return u.place_order(TransactionType.Buy,  # transaction_type
                  u.get_instrument_by_symbol('NSE_EQ', symbol),  # instrument
                  1,  # quantity
                  OrderType.Market,  # order_type
                  ProductType.Intraday,  # product_type
                  0.0,  # price
                  None,  # trigger_price
                  0,  # disclosed_quantity
                  DurationType.DAY,  # duration
                  None,  # stop_loss
                  None,  # square_off
                  None)  # trailing_ticks

def stoplossforbuy(symbol, trigger):
    return u.place_order(TransactionType.Sell,  # transaction_type
                 u.get_instrument_by_symbol('NSE_EQ', symbol),  # instrument
                 1,  # quantity
                 OrderType.StopLossMarket,  # order_type
                 ProductType.Intraday,  # product_type
                 0.0,  # price
                 trigger,  # trigger_price
                 0,  # disclosed_quantity
                 DurationType.DAY,  # duration
                 None,  # stop_loss
                 None,  # square_off
                 None)  # trailing_ticks

def sell(symbol):
    return u.place_order(TransactionType.Sell,  # transaction_type
                  u.get_instrument_by_symbol('NSE_EQ', symbol),  # instrument
                  1,  # quantity
                  OrderType.Market,  # order_type
                  ProductType.Intraday,  # product_type
                  0.0,  # price
                  None,  # trigger_price
                  0,  # disclosed_quantity
                  DurationType.DAY,  # duration
                  None,  # stop_loss
                  None,  # square_off
                  None)  # trailing_ticks

def stoplossforsell(symbol, trigger):
    return u.place_order(TransactionType.Buy,  # transaction_type
                 u.get_instrument_by_symbol('NSE_EQ', symbol),  # instrument
                 1,  # quantity
                 OrderType.StopLossMarket,  # order_type
                 ProductType.Intraday,  # product_type
                 0.0,  # price
                 trigger,  # trigger_price
                 0,  # disclosed_quantity
                 DurationType.DAY,  # duration
                 None,  # stop_loss
                 None,  # square_off
                 None)  # trailing_ticks

#This is a short sell stratergy.
#Stocks are sold when there is three consecutive bullish candle appear
def decision(temp):
    if temp[-2]["close"] > temp[-2]["open"] and temp[-1]["close"] < temp[-1]["open"] and temp[-1]["high"] < temp[-2]["close"] and temp[-1]["close"] < temp[-2]["open"] and temp[-1]["low"] < temp[-2]["low"] and movingAve5m(script) > temp[-1]["cp"]:
        print(sell(script))
        print(stoplossforsell(script, round(0.05 * round(float(temp[-3]["low"]) / 0.05), 2)))
        sold[script] = temp[-1]["cp"]

    if temp[-2]["close"] < temp[-2]["open"] and temp[-1]["close"] > temp[-1]["open"] and temp[-1]["high"] > temp[-2]["close"] and temp[-1]["close"] > temp[-2]["open"] and temp[-1]["low"] > temp[-2]["low"] and movingAve5m(script) < temp[-1]["cp"]:
        print(buy(script))
        print(stoplossforbuy(script, round(0.05 * round(float(temp[-3]["low"]) / 0.05), 2)))
        bought[script] = temp[-1]["cp"]

bought = {}
sold = {}
profit = 0
bucket = ["ABAN", "ADANIENT", "ADANIPORTS", "ADANIPOWER", "ARCOTECH", "AXISBANK", "BOMDYEING", "BPL", "DAAWAT", "EKC", "ENGINERSIN",
          "FCONSUMER", "FEDERALBNK", "FORTIS", "GAIL", "GITANJALI", "HBLPOWER", "HCC", "HDIL", "HFCL", "HINDOILEXP",
          "IBREALEST", "ICICIBANK", "INFIBEAM", "INFY", "ITC", "JETAIRWAYS", "JINDALSTEL", "JISLJALEQS",
          "JKPAPER", "JSWENERGY", "L&TFH", "LUPIN", "M&MFIN", "MARKSANS", "ONGC", "PCJEWELLER", "PNB", "PRAKASH", "PURVA", "RELIANCE",
          "RHFL", "SBIN", "SETCO", "SOUTHBANK", "TATAGLOBAL", "TATAMOTORS", "TATASTEEL", "TECHM", "TV18BRDCST", "VEDL"]

for script in bucket:
    print("~~~~~~~~~~~~~~~~~~~~~~~ \n Now the time is: %s" %datetime.datetime.now().time())
    print("Checking for BlackCrow for %s" % script)
    decision(historicData(script, "13/12/2017", "13/12/2017"))

for script in bucket:
    print("~~~~~~~~~~~~~~~~~~~~~~~ \n Now the time is: %s" %datetime.datetime.now().time())
    print("Checking for 10 min MA Crossover for %s" % script)
    tenMMACross(historicData(script, "13/12/2017", "13/12/2017"))

print(u.get_positions())
