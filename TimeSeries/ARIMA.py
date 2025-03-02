import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
from math import sqrt
from itertools import product

def prepare_data(df):
    if 'Date' not in df.columns:
        df = df.reset_index()
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    return df.sort_index()

def find_best_arima_order(data, max_p=3, max_d=2, max_q=3):
    best_aic = float("inf")
    best_order = None
    for p, d, q in product(range(max_p+1), range(max_d+1), range(max_q+1)):
        try:
            model = ARIMA(data, order=(p, d, q))
            results = model.fit()
            if results.aic < best_aic:
                best_aic = results.aic
                best_order = (p, d, q)
        except:
            continue
    return best_order

def arima_model_and_forecast(df, ticker, forecast_steps=30):
    df = prepare_data(df)
    data = df['Close']
    
    order = find_best_arima_order(data)
    print(f"Best ARIMA order for {ticker}: {order}")
    
    train_size = int(len(data) * 0.8)
    train, test = data[:train_size], data[train_size:]
    
    model = ARIMA(train, order=order)
    results = model.fit()
    
    predictions = results.forecast(steps=len(test))
    rmse = sqrt(mean_squared_error(test, predictions))
    print(f'Test RMSE: {rmse}')
    
    future_forecast = results.forecast(steps=forecast_steps)
    
    plt.figure(figsize=(12, 6))
    plt.plot(data.index, data, label='Actual')
    plt.plot(test.index, predictions, color='red', label='Predictions')
    plt.plot(future_forecast.index, future_forecast, color='green', label='Forecast')
    plt.title(f'ARIMA Model for {ticker} Stock Prices')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'data/pics/{ticker}_arima_forecast.pdf')
    plt.close()
    
    return results, future_forecast

def main():
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
