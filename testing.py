import time
import pandas_datareader as pdr
import yfinance as yf
import pandas as pd
import requests
import sqlite3
import json

def get_stock_prices(ticker, period="1m", retries=3, delay=5):
    for attempt in range(retries):
        try:
            # Try yfinance first
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            if not hist.empty:
                stock_prices = hist.reset_index().to_dict('records')
                df = pd.DataFrame(stock_prices)
                df['Date'] = pd.to_datetime(df['Date'])
                df.to_json(f'data/stock/stock_prices_{ticker}.json', orient='records', date_format='iso')
                return df
            
            # If yfinance fails, try pandas_datareader
            end_date = pd.Timestamp.now()
            start_date = end_date - pd.Timedelta(period)
            df = pdr.get_data_yahoo(ticker, start=start_date, end=end_date)
            if not df.empty:
                df = df.reset_index()
                df.to_json(f'data/stock/stock_prices_{ticker}.json', orient='records', date_format='iso')
                return df
            
            raise ValueError(f"No price data found for ticker {ticker} (period={period})")
        
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for ticker '{ticker}'. Error: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"Failed to get data for ticker '{ticker}' after {retries} attempts.")
                return None

# # Usage
# tickers = ["YUM", "MCD", "CMG", "SBUX", "JACK"]  # Add your tickers here

# for ticker in tickers:
#     print(f"Processing {ticker}")
#     stock_data = get_stock_prices(ticker)
#     if stock_data is not None:
#         print(f"Successfully retrieved data for {ticker}")
#     else:
#         print(f"Failed to retrieve data for {ticker}")
#     time.sleep(2)  # Add a small delay between requests to avoid rate limiting





dat = yf.Ticker("MSFT")
print("Info:", dat.info)
print("Calendar:", dat.calendar)
print("Analyst Price Targets:", dat.analyst_price_targets)
print("Quarterly Income Statement:", dat.quarterly_income_stmt)
print("History:", dat.history(period='1mo'))
print("Option Chain Calls:", dat.option_chain(dat.options[0]).calls)