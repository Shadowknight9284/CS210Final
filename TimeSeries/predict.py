import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

def load_and_prepare_data(ticker):
    df = pd.read_csv(f'data/big4stocks/stock{ticker}.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df.sort_index(inplace=True)
    return df

def simple_moving_average(data, window=30, forecast_periods=30):
    sma = data['Close'].rolling(window=window).mean()
    forecast = [sma.iloc[-1]] * forecast_periods
    return sma, pd.Series(forecast, index=pd.date_range(start=data.index[-1] + pd.Timedelta(days=1), periods=forecast_periods))

def exponential_moving_average(data, span=30, forecast_periods=30):
    ema = data['Close'].ewm(span=span, adjust=False).mean()
    forecast = [ema.iloc[-1]] * forecast_periods
    return ema, pd.Series(forecast, index=pd.date_range(start=data.index[-1] + pd.Timedelta(days=1), periods=forecast_periods))

def linear_regression(data, forecast_periods=30):
    X = np.array(range(len(data))).reshape(-1, 1)
    y = data['Close'].values
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    predictions = model.predict(X)
    
    future_X = np.array(range(len(data), len(data) + forecast_periods)).reshape(-1, 1)
    forecast = model.predict(future_X)
    
    return pd.Series(predictions, index=data.index), pd.Series(forecast, index=pd.date_range(start=data.index[-1] + pd.Timedelta(days=1), periods=forecast_periods))

def plot_predictions(data, predictions, forecast, title):
    plt.figure(figsize=(12, 6))
    plt.plot(data.index, data['Close'], label='Actual')
    plt.plot(predictions.index, predictions, label='Predictions')
    plt.plot(forecast.index, forecast, label='Forecast')
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'data/pics/{title.replace(" ", "_")}.pdf')
    plt.close()

def main():
    tickers = ['CMG', 'MCD', 'SBUX']
    for ticker in tickers:
        print(f"\nProcessing {ticker}")
        data = load_and_prepare_data(ticker)
        
        # Simple Moving Average
        sma, sma_forecast = simple_moving_average(data)
        plot_predictions(data, sma, sma_forecast, f'{ticker} Simple Moving Average')
        
        # Exponential Moving Average
        ema, ema_forecast = exponential_moving_average(data)
        plot_predictions(data, ema, ema_forecast, f'{ticker} Exponential Moving Average')
        
        # Linear Regression
        lr_pred, lr_forecast = linear_regression(data)
        plot_predictions(data, lr_pred, lr_forecast, f'{ticker} Linear Regression')

if __name__ == "__main__":
    main()
