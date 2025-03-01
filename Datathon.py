import requests
import pandas as pd
import numpy as np 
import json
import matplotlib.pyplot as plt
import yfinance as yf
import sqlite3

headers = {'User-Agent': "pranavtikkawar@gmail.com"}
companyTickers = requests.get('https://www.sec.gov/files/company_tickers.json', headers=headers)
companyData = pd.DataFrame.from_dict(companyTickers.json(), orient='index')
companyData['cik_str'] = companyData['cik_str'].apply(lambda x: str(x).zfill(10))
companyData.to_csv('companyData.csv', index=False)
