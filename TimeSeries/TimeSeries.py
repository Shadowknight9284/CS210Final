import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from pmdarima import auto_arima
from sklearn.metrics import mean_squared_error
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
    df['200 Day MA'] = df['Close'].rolling(window=200).mean()
    
    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Close'], label='Close Price', color='blue')
    plt.plot(df.index, df['50 Day MA'], label='50 Day MA', color='red')
    plt.plot(df.index, df['200 Day MA'], label='200 Day MA', color='green')
    plt.title(f'Stock Price and Moving Averages of {ticker}')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.grid(True)
    
    # Save the plot as a PDF
    plt.savefig(f'data/pics/{ticker}_moving_averages.pdf')
    plt.close()
    


def prepare_data(df):
    # Check if 'Date' is in columns, if not, reset index
    if 'Date' not in df.columns:
        df = df.reset_index()
    
    # Convert 'Date' column to datetime and set as index
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    
    # Sort the dataframe by date
    df = df.sort_index()
    
    return df

def find_best_arima_order(data):
    # Use auto_arima to find the best ARIMA order
    model = auto_arima(data, start_p=1, start_q=1, max_p=3, max_q=3, m=1,
                       start_P=0, seasonal=False, d=1, D=1, trace=True,
                       error_action='ignore', suppress_warnings=True, stepwise=True)
    return model.order

def arima_model_and_forecast(df, ticker, forecast_steps=30):
    # Prepare data
    df = prepare_data(df)
    
    # Use 'Close' prices for modeling
    data = df['Close']
    
    # Find the best ARIMA order
    order = find_best_arima_order(data)
    print(f"Best ARIMA order for {ticker}: {order}")
    
    # Split data into train and test sets
    train_size = int(len(data) * 0.8)
    train, test = data[:train_size], data[train_size:]
    
    # Fit ARIMA model
    model = ARIMA(train, order=order)
    results = model.fit()
    
    # Make predictions on test set
    predictions = results.forecast(steps=len(test))
    
    # Calculate RMSE
    rmse = sqrt(mean_squared_error(test, predictions))
    print(f'Test RMSE: {rmse}')
    
    # Forecast future values
    future_forecast = results.forecast(steps=forecast_steps)
    
    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(data.index, data, label='Actual')
    plt.plot(test.index, predictions, color='red', label='Predictions')
    plt.plot(future_forecast.index, future_forecast, color='green', label='Forecast')
    plt.title(f'ARIMA Model for {ticker} Stock Prices')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.grid(True)
    
    # Save the plot as a PDF
    plt.savefig(f'data/pics/{ticker}_arima_forecast.pdf')
    plt.close()
    
    return results, future_forecast



def main():
    # Plot stock data for each company
    tickers = ['CMG', 'MCD', 'SBUX']
    for ticker in tickers:
        try:
            df = pd.read_csv(f'data/big4stocks/stock{ticker}.csv')
            plot_stock_data(df, ticker)
            moving_average(df, ticker)
            print(f"Successfully processed {ticker}")
        except Exception as e:
            print(f"Error processing {ticker}: {str(e)}")
            
            
    tickers = ['CMG', 'MCD', 'SBUX']
    for ticker in tickers:
        try:
            df = pd.read_csv(f'data/big4stocks/stock{ticker}.csv')
            print(f"\nProcessing {ticker}")
            model, forecast = arima_model_and_forecast(df, ticker)
            print(f"Future forecast for {ticker}:")
            print(forecast)
        except Exception as e:
            print(f"Error processing {ticker}: {str(e)}")

if __name__ == "__main__":
    main()
