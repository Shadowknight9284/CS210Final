import requests
import pandas as pd
import numpy as np 
import json
import matplotlib.pyplot as plt
from alpha_vantage.timeseries import TimeSeries
import yfinance as yf
import sqlite3
from datetime import datetime, timedelta

headers = {'User-Agent': "pranavtikkawar@gmail.com"}
companyTickers = requests.get('https://www.sec.gov/files/company_tickers.json', headers=headers)
companyData = pd.DataFrame.from_dict(companyTickers.json(), orient='index')
companyData['cik_str'] = companyData['cik_str'].apply(lambda x: str(x).zfill(10))
companyData.to_csv('companyData.csv', index=False)

def get_stock_prices_alpha(ticker, time_delta='10y', outputsize='full'):
    # Your Alpha Vantage API key
    api_key = 'PNMKBBX1K41GGD47'
    
    # Create a TimeSeries object
    ts = TimeSeries(key=api_key, output_format='pandas')
    
    # Calculate start_date based on time_delta
    if time_delta.endswith('y'):
        years = int(time_delta[:-1])
        start_date = datetime.now() - timedelta(days=365*years)
    elif time_delta.endswith('d'):
        days = int(time_delta[:-1])
        start_date = datetime.now() - timedelta(days=days)
    else:
        raise ValueError("Invalid time_delta format. Use 'Xy' for years or 'Xd' for days, e.g., '5y' or '180d'")
    
    try:
        # Get daily data
        data, meta_data = ts.get_daily(symbol=ticker, outputsize=outputsize)
        
        # Check if 'Date' is in the index
        if 'Date' not in data.index.names:
            # If 'Date' is not in the index, it might be a column
            if 'Date' in data.columns:
                data = data.set_index('Date')
            else:
                # If 'Date' is neither in index nor columns, create a date index
                data.index = pd.date_range(end=pd.Timestamp.now(), periods=len(data), freq='D')[::-1]
                data.index.name = 'Date'
        
        # Rename columns
        data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        
        # Reset index to make date a column
        data = data.reset_index()
        
        # Convert 'Date' to datetime if it's not already
        data['Date'] = pd.to_datetime(data['Date'])
        
        # Filter data based on start_date
        data = data[data['Date'] >= start_date]
        
        # Sort by date
        data = data.sort_values('Date')
        
        # Save to JSON
        data.to_json(f'data/big4stock/stock_prices_{ticker}_{time_delta}.json', orient='records', date_format='iso')
        
        return data
    
    except Exception as e:
        print(f"Error fetching data for {ticker}: {str(e)}")
        return None

def get_stock_prices(ticker, period="5y"):
    stock = yf.Ticker(ticker)
    try:
        hist = stock.history(period=period)
        if hist.empty:
            raise ValueError(f"No price data found for ticker {ticker} (period={period})")
        stock_prices = [{"Date": str(date), "Open": open, "Close": close, "High": high, "Low": low, "Volume": volume } for date, open, close, high, low, volume in zip(hist.index, hist["Open"], hist["Close"], hist["High"], hist["Low"], hist["Volume"])]
        stock_prices = pd.DataFrame(stock_prices)
        stock_prices['Date'] = pd.to_datetime(stock_prices['Date'])
        stock_prices.to_json(f'data/stock/stock_prices_{ticker}.json', orient='records', date_format='iso')
        return stock_prices
    except Exception as e:
        print(f"Failed to get ticker '{ticker}' reason: {e}")
        return None

def get_MetaData(ticker):
    try:
        if ticker not in companyData['ticker'].values:
            raise ValueError(f"Ticker {ticker} not found in companyData.csv")
        cik = companyData[companyData['ticker'] == ticker].cik_str[0]
        filingMetadata = requests.get(f'https://data.sec.gov/submissions/CIK{cik}.json', headers=headers)
        return filingMetadata.json()
    except Exception as e:
        print(f"Error processing ticker {ticker}: {e}")
        return None

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

def get_Land_Data(ticker):
    land_terms = ["Land", "LandAndImprovements", "RealEstate", "PropertyAndEquipment", "LandAndBuildings", "RealProperty", "LandHeldForDevelopment", "InvestmentProperty"]
    
    for term in land_terms:
        try:
            land_data = get_LineItems(ticker, term)
            if land_data:
                return land_data, term
        except KeyError:
            continue
    
    return None, None

def get_Data(ticker):
    land_data, land_term = get_Land_Data(ticker)
    
    if not land_data:
        print(f"No specific land data found for {ticker}. Checking PP&E...")
        try:
            ppe = get_LineItems(ticker, "PropertyPlantAndEquipmentNet")
            if ppe:
                print(f"PP&E data found for {ticker}. Land may be included in this figure.")
            else:
                print(f"No PP&E data found for {ticker}.")
        except KeyError:
            print(f"No PP&E data found for {ticker}.")

    try:
        revenue = get_LineItems(ticker, "Revenues")
    except KeyError:
        try:
            revenue = get_LineItems(ticker, "SalesRevenueNet")
        except KeyError:
            revenue = None

    try:
        net_income = get_LineItems(ticker, "NetIncomeLoss")
    except KeyError:
        net_income = None

    try:
        operating_income = get_LineItems(ticker, "OperatingIncomeLoss")
    except KeyError:
        operating_income = None

    try:
        ppe = get_LineItems(ticker, "PropertyPlantAndEquipmentGross")
    except KeyError:
        ppe = None

    try:
        accumulated_depreciation = get_LineItems(ticker, "AccumulatedDepreciationDepletionAndAmortization")
    except KeyError:
        accumulated_depreciation = None

    try:
        operating_lease_liability = get_LineItems(ticker, "OperatingLeaseLiability")
    except KeyError:
        operating_lease_liability = None

    try:
        cogs = get_LineItems(ticker, "CostOfGoodsSold")
    except KeyError:
        try:
            cogs = get_LineItems(ticker, "CostOfRevenue")
        except KeyError:
            cogs = None

    try:
        depreciation_amortization = get_LineItems(ticker, "DepreciationAndAmortization")
    except KeyError:
        depreciation_amortization = None

    try:
        capex = get_LineItems(ticker, "PaymentsToAcquirePropertyPlantAndEquipment")
    except KeyError:
        capex = None

    try:
        total_assets = get_LineItems(ticker, "Assets")
    except KeyError:
        total_assets = None

    # stock_prices = get_stock_prices(ticker)

    data = [
        {
            "Ticker": ticker,
            "Land": land_data,
            "LandTerm": land_term,
            "Revenue": revenue,
            "NetIncome": net_income,
            "OperatingIncome": operating_income,
            "PropertyPlantAndEquipment": ppe,
            "AccumulatedDepreciation": accumulated_depreciation,
            "OperatingLeaseLiability": operating_lease_liability,
            "CostOfGoodsSold": cogs,
            "DepreciationAndAmortization": depreciation_amortization,
            "CapitalExpenditures": capex,
            "TotalAssets": total_assets
        },
    ]
    return data

def to_JSON(tickerArray, exitJson = 'stock_data.json'):
    all_data = []
    for ticker in tickerArray:
        data = get_Data(ticker)
        all_data.extend(data)  
    with open(exitJson, 'w') as json_file:  
        json.dump(all_data, json_file, indent=4)
        
def to_SQLite(tickerArray):
    all_data = []
    for ticker in tickerArray:
        data = get_Data(ticker)
        all_data.extend(data)
    conn = sqlite3.connect('stock_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS stock_data 
                (Ticker TEXT, Land TEXT, Revenue TEXT, NetIncome TEXT, 
                OperatingIncome TEXT, PropertyPlantAndEquipment TEXT, 
                AccumulatedDepreciation TEXT, OperatingLeaseLiability TEXT, 
                CostOfGoodsSold TEXT, DepreciationAndAmortization TEXT, 
                CapitalExpenditures TEXT, TotalAssets TEXT, StockPrices TEXT)''')
    for data in all_data:
        c.execute('''INSERT INTO stock_data VALUES 
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                    (data['Ticker'], str(data['Land']), str(data['Revenue']), 
                    str(data['NetIncome']), str(data['OperatingIncome']), 
                    str(data['PropertyPlantAndEquipment']), 
                    str(data['AccumulatedDepreciation']), 
                    str(data['OperatingLeaseLiability']), 
                    str(data['CostOfGoodsSold']), 
                    str(data['DepreciationAndAmortization']), 
                    str(data['CapitalExpenditures']), 
                    str(data['TotalAssets']), 
                    str(data['StockPrices'])))
    conn.commit()
    conn.close()



tickers = [
    'CMG',
    'MCD',
    'SBUX',
    'YUM'
]

for ticker in tickers:
    print(f"Processing {ticker}")
    get_stock_prices_alpha([ticker], "10y")
    
    


# mcd = get_CompanyFacts("MCD")
# with open('data/sec/mcd.json', 'w') as f:
#     json.dump(mcd, f, indent=4)
    
    
# MCD_Land_df = get_LineItems_PD("MCD", "Land")
# MCD_Revenues_df = get_LineItems_PD("MCD", "Revenues")


    