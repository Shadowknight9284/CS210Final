import requests
import pandas as pd
from datetime import datetime, timedelta
import os

def get_stock_data(ticker, start_date, end_date):
    # Convert dates to Unix timestamp
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())
    
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?period1={start_timestamp}&period2={end_timestamp}&interval=1d"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    if 'chart' not in data or 'result' not in data['chart'] or not data['chart']['result']:
        print(f"No data available for {ticker}")
        return None
    
    stock_data = data['chart']['result'][0]
    
    df = pd.DataFrame({
        'Date': pd.to_datetime(stock_data['timestamp'], unit='s'),
        'Open': stock_data['indicators']['quote'][0]['open'],
        'High': stock_data['indicators']['quote'][0]['high'],
        'Low': stock_data['indicators']['quote'][0]['low'],
        'Close': stock_data['indicators']['quote'][0]['close'],
        'Volume': stock_data['indicators']['quote'][0]['volume']
    })
    
    df.set_index('Date', inplace=True)
    return df

def save_to_csv(data, ticker):
    if data is None or data.empty:
        print(f"No data to save for {ticker}")
        return
    
    output_dir = "data/big4stocks"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    filename = os.path.join(output_dir, f"stock{ticker}.csv")
    data.to_csv(filename)
    print(f"Data for {ticker} saved to {filename}")

def main():
    tickers = [
        'CMG',
        'MCD',
        'SBUX',
        'YUM'
    ]

    end_date = datetime.now()
    start_date = end_date - timedelta(days=3652)  # Approximately 10 years

    for ticker in tickers:
        print(f"Fetching data for {ticker}...")
        stock_data = get_stock_data(ticker, start_date, end_date)
        save_to_csv(stock_data, ticker)
        if stock_data is not None and not stock_data.empty:
            print(f"Completed fetching data for {ticker}")
        print("------------------------")

if __name__ == "__main__":
    main()
