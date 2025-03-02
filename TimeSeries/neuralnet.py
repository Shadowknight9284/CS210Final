import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras.optimizers import Adam

def load_and_prepare_data(ticker):
    df = pd.read_csv(f'data/big4stocks/stock{ticker}.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df.sort_index(inplace=True)
    return df

def create_sequences(data, seq_length):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:(i + seq_length)])
        y.append(data[i + seq_length])
    return np.array(X), np.array(y)

def build_lstm_model(seq_length):
    model = Sequential([
        LSTM(50, activation='relu', input_shape=(seq_length, 1), return_sequences=True),
        LSTM(50, activation='relu', return_sequences=False),
        Dense(25),
        Dense(1)
    ])
    model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
    return model

def train_and_predict(data, seq_length=60, forecast_days=30):
    # Normalize the data
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data['Close'].values.reshape(-1, 1))

    # Create sequences
    X, y = create_sequences(scaled_data, seq_length)

    # Split into train and test sets
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    # Build and train the model
    model = build_lstm_model(seq_length)
    model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.1, verbose=0)

    # Make predictions
    train_predict = model.predict(X_train)
    test_predict = model.predict(X_test)

    # Inverse transform predictions
    train_predict = scaler.inverse_transform(train_predict)
    test_predict = scaler.inverse_transform(test_predict)

    # Forecast future values
    last_sequence = scaled_data[-seq_length:]
    forecast = []
    for _ in range(forecast_days):
        next_pred = model.predict(last_sequence.reshape(1, seq_length, 1))
        forecast.append(next_pred[0, 0])
        last_sequence = np.roll(last_sequence, -1)
        last_sequence[-1] = next_pred

    forecast = scaler.inverse_transform(np.array(forecast).reshape(-1, 1))

    return train_predict, test_predict, forecast, train_size, seq_length

def plot_predictions(data, train_predict, test_predict, forecast, ticker, train_size, seq_length):
    plt.figure(figsize=(12, 6))
    plt.plot(data.index, data['Close'], label='Actual')
    
    # Correct indices for train predictions
    train_indices = data.index[seq_length:seq_length+len(train_predict)]
    plt.plot(train_indices, train_predict.flatten(), label='Train Predictions')
    
    # Correct indices for test predictions
    test_indices = data.index[seq_length+train_size:seq_length+train_size+len(test_predict)]
    plt.plot(test_indices, test_predict.flatten(), label='Test Predictions')
    
    # Forecast dates
    forecast_dates = pd.date_range(start=data.index[-1] + pd.Timedelta(days=1), periods=len(forecast))
    plt.plot(forecast_dates, forecast.flatten(), label='Forecast')
    
    plt.title(f'{ticker} LSTM Neural Network Predictions')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'data/pics/{ticker}_LSTM_predictions.pdf')
    plt.close()

def main():
    tickers = ['CMG', 'MCD', 'SBUX']
    for ticker in tickers:
        print(f"\nProcessing {ticker}")
        data = load_and_prepare_data(ticker)
        train_predict, test_predict, forecast, train_size, seq_length = train_and_predict(data)
        plot_predictions(data, train_predict, test_predict, forecast, ticker, train_size, seq_length)

if __name__ == "__main__":
    main()