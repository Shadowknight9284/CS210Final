import requests
import pandas as pd
import numpy as np 
import json
import matplotlib.pyplot as plt
import yfinance as yf
import sqlite3
import seaborn as sns 
import DataGenerator as dg

c = sqlite3.connect('stock_data.db')
cursor = c.cursor()
# Fetch data from the database
cursor.execute("SELECT * FROM stock_data")
data = cursor.fetchall()
# Convert data to DataFrame
df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])
# Close the connection
c.close()

# Read JSON file
with open('stock_data.json') as f:
    json_data = json.load(f)

# Convert JSON data to DataFrame
df_json = pd.DataFrame(json_data)
        
Revenue_10K = []
for name in df_json['Revenue']:
    for i in range(len(name)):
        if name[i]['form'] == '10-K':
            Revenue_10K.append( [name[i]['fy'], name[i]['val']])

Land_10K = []
for name in df_json['Land']:
    for i in range(len(name)):
        if name[i]['form'] == '10-K':
            Land_10K.append( [name[i]['fy'], name[i]['val']])

combined_data = []
for i in range(len(Revenue_10K)):
    for j in range(len(Land_10K)):
        if Revenue_10K[i][0] == Land_10K[j][0]:
            combined_data.append([Revenue_10K[i][0], Revenue_10K[i][1], Land_10K[j][1]])
        
print(combined_data)