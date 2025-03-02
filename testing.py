from polygon import RESTClient
import pandas as pd
from datetime import datetime, timedelta
import time

def get_stock_prices(ticker, time_delta='1y', api_key='p59hS78e_nfVaO3aUBaLepJ_37aeN0Oj'):
    # Create a RESTClient instance
    client = RESTClient(api_key)
    
    # Calculate start_date and end_date based on time_delta
    end_date = datetime.now()
    if time_delta.endswith('y'):
        years = int(time_delta[:-1])
        start_date = end_date - timedelta(days=365*years)
    elif time_delta.endswith('d'):
        days = int(time_delta[:-1])
        start_date = end_date - timedelta(days=days)
    else:
        raise ValueError("Invalid time_delta format. Use 'Xy' for years or 'Xd' for days, e.g., '5y' or '180d'")
    
    try:
        # Get daily data
        aggs = client.get_aggs(ticker, 1, "day", start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        
        # Convert to pandas DataFrame
        data = pd.DataFrame([
            {
                'Date': pd.Timestamp.fromtimestamp(agg.timestamp/1000),
                'Open': agg.open,
                'High': agg.high,
                'Low': agg.low,
                'Close': agg.close,
                'Volume': agg.volume
            } for agg in aggs
        ])
        
        # Sort by date
        data = data.sort_values('Date')
        
        # Save to JSON
        data.to_json(f'data/polygon/stock_prices_{ticker}_{time_delta}.json', orient='records', date_format='iso')
        
        return data
    
    except Exception as e:
        print(f"Error fetching data for {ticker}: {str(e)}")
        return None


tickers = [
    "DPZ", 
    "DRI", 
    "JACK", 
    "MCD", 
    "PZZA", 
    "QSR", 
    "RRGB", 
    "SBUX", 
    "SHAK", 
    "WEN", 
    "WING", 
    "YUM"
]

for ticker in tickers:
    print(f"Processing {ticker}")
    get_stock_prices(ticker, "10y")