import os
import requests
import pandas as pd
import numpy as np 
import json
import matplotlib.pyplot as plt
import yfinance as yf
import sqlite3
import seaborn as sns 
import DataGenerator as dg

def save_json_to_file(json_data, file_path):
    with open(file_path, 'w') as f:
        json.dump(json_data, f, indent=4)

def plot_from_json(json_data):
    # Convert JSON data to DataFrame
    df_json = pd.DataFrame(json_data)
            
    Revenue_10K = []
    for name in df_json['Revenue']:
        for i in range(len(name)):
            if name[i]['form'] == '10-K':
                Revenue_10K.append([name[i]['fy'], name[i]['val']])
    
    Land_10K = []
    for name in df_json['Land']:
        for i in range(len(name)):
            if name[i]['form'] == '10-K':
                Land_10K.append([name[i]['fy'], name[i]['val']])
    
    combined_data = []
    for i in range(len(Revenue_10K)):
        for j in range(len(Land_10K)):
            if Revenue_10K[i][0] == Land_10K[j][0]:
                combined_data.append([Revenue_10K[i][0], Revenue_10K[i][1], Land_10K[j][1]])
    
    # Extract data for plotting
    year = [data[0] for data in combined_data]
    x = [data[1] for data in combined_data]
    y = [data[2] for data in combined_data]

    plt.scatter(x, y, c=year)
    plt.xlabel('Revenue')
    plt.ylabel('Land')
    plt.title('Scatter Plot')
    plt.colorbar(label='Year')

    # Add line of best fit
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    plt.plot(x, p(x), color='red')

    # Calculate R^2
    residuals = y - p(x)
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    r_squared = 1 - (ss_res / ss_tot)

    # Display formula and R^2
    formula = f'y = {z[0]}x + {z[1]}'
    r_squared_text = f'R^2 = {r_squared:.4f}'
    plt.text(0.05, 0.95, formula, transform=plt.gca().transAxes, fontsize=10, verticalalignment='top')
    plt.text(0.05, 0.90, r_squared_text, transform=plt.gca().transAxes, fontsize=10, verticalalignment='top')

    plt.show()

# Example usage
tickers = ['CMG', 'MCD', 'SBUX']

os.makedirs('data/big4plot', exist_ok=True)

for ticker in tickers:
    json_file_path = f'data/big4/stock_data{ticker}.json'
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as f:
            json_data = json.load(f)
        
        plot_from_json(json_data)
    else:
        print(f"File not found: {json_file_path}")