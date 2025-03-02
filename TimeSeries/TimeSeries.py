import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import sqrt

def plot_stock_data(df, ticker):
    # Check if 'Date' is in columns, if not, reset index
    if 'Date' not in df.columns:
        df = df.reset_index()
    
    # Convert 'Date' column to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Set 'Date' as index
    df.set_index('Date', inplace=True)
    
    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Close'], label='Close Price', color='blue')
    plt.title(f'Stock Price of {ticker}')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.grid(True)
    
    # Save the plot as a PDF
    plt.savefig(f'data/pics/{ticker}_stock_price.pdf')
    plt.close()

def moving_average(df, ticker):
    # Check if 'Date' is in columns, if not, reset index
    if 'Date' not in df.columns:
        df = df.reset_index()
    
    # Convert 'Date' column to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Set 'Date' as index
    df.set_index('Date', inplace=True)
    
    # Calculate daily returns
    df['Daily Return'] = df['Close'].pct_change()
    
    # Calculate moving averages
    df['50 Day MA'] = df['Close'].rolling(window=50).mean()
    df['100 Day MA'] = df['Close'].rolling(window=100).mean()
    df['200 Day MA'] = df['Close'].rolling(window=200).mean()
    
    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Close'], label='Close Price', color='blue')
    plt.plot(df.index, df['50 Day MA'], label='50 Day MA', color='green')
    plt.plot(df.index, df['100 Day MA'], label='100 Day MA', color='orange') 
    plt.plot(df.index, df['200 Day MA'], label='200 Day MA', color='purple')
    plt.title(f'Stock Price and Moving Averages of {ticker}')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.grid(True)
    
    # Save the plot as a PDF
    plt.savefig(f'data/pics/{ticker}_moving_averages.pdf')
    plt.close()
    


def main():
    # Plot stock data for each company
    tickers = ['CMG', 'MCD', 'SBUX']
    for ticker in tickers:
        try:
            df = pd.read_csv(f'data/big4stocks/stock{ticker}.csv')
            moving_average(df, ticker)
            print(f"Successfully processed {ticker}")
        except Exception as e:
            print(f"Error processing {ticker}: {str(e)}")
        

if __name__ == "__main__":
    main()
