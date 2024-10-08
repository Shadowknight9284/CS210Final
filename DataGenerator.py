import requests
import pandas as pd
import numpy as np 
import json
import matplotlib.pyplot as plt
import yfinance as yf
import sqlite3

headers = {'User-Agent': "pranavtikkawar@gmail.com"}
companyTickers = requests.get('https://www.sec.gov/files/company_tickers.json', headers=headers)
companyData = pd.DataFrame.from_dict(companyTickers.json(), orient='index')
companyData['cik_str'] = companyData['cik_str'].apply(lambda x: str(x).zfill(10))
companyData.to_csv('companyData.csv', index=False)

def get_stock_prices(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="5y")
    stock_prices = [{"Date": str(date.date()), "Open": open, "Close": close, "High": high, "Low": low, "Volume": volume } for date, open, close, high, low, volume in zip(hist.index, hist["Open"], hist["Close"], hist["High"], hist["Low"], hist["Volume"])]
    return stock_prices

def get_MetaData(ticker):
    cik = companyData[companyData['ticker'] == ticker].cik_str[0]
    filingMetadata = requests.get(f'https://data.sec.gov/submissions/CIK{cik}.json', headers=headers)
    return filingMetadata.json()

def get_CompanyFacts(ticker):
    cik = companyData[companyData['ticker'] == ticker].cik_str[0]
    companyFacts = requests.get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json', headers=headers)
    return companyFacts.json()

def get_LineItems_PD(ticker, form):
    companyFacts = get_CompanyFacts(ticker)
    final_fy = []
    final_val = []
    for i in companyFacts['facts']['us-gaap'][form]['units']['USD']:
        final_fy.append(i['fy'])
        final_val.append(i['val'])
    final = pd.DataFrame({'fy': final_fy, 'val': final_val})
    return final

def get_LineItems(ticker, form):
    companyFacts = get_CompanyFacts(ticker)
    companyData = companyFacts['facts']['us-gaap'][form]['units']['USD']
    return companyData


def get_Data(ticker):
    data = [
        {
            "Ticker": ticker,
            "Land": get_LineItems(ticker, "Land"),
            "Revenue": get_LineItems(ticker, "Revenues"),
            "NetIncome": get_LineItems(ticker, "NetIncomeLoss"),
            "OperatingIncome": get_LineItems(ticker, "OperatingIncomeLoss"),
            "StockPrices": get_stock_prices(ticker)
        },
    ]
    return data


def to_JSON(tickerArray):
    all_data = []
    for ticker in tickerArray:
        data = get_Data(ticker)
        all_data.extend(data)  
    with open('stock_data.json', 'w') as json_file:  
        json.dump(all_data, json_file, indent=4)
        
def to_SQLite(tickerArray):
    all_data = []
    for ticker in tickerArray:
        data = get_Data(ticker)
        all_data.extend(data)
    conn = sqlite3.connect('stock_data.db')
    c = conn.cursor()
    c.execute('CREATE TABLE stock_data (Ticker TEXT, Land TEXT, Revenue TEXT, NetIncome TEXT, OperatingIncome TEXT, EPS TEXT, StockPrices TEXT)')
    for data in all_data:
        c.execute('INSERT INTO stock_data VALUES (?, ?, ?, ?, ?, ?, ?)', (data['Ticker'], str(data['Land']), str(data['Revenue']), str(data['NetIncome']), str(data['OperatingIncome']), str(data['EPS']), str(data['StockPrices'])))
    conn.commit()
    conn.close()

        
# tickerArray = ["YUM", "MCD", "CMG", "SBUX", "JACK"]
tickerArray = ["MCD"]
to_JSON(tickerArray)


# MCD_Land_df = get_LineItems_PD("MCD", "Land")
# MCD_Revenues_df = get_LineItems_PD("MCD", "Revenues")


    