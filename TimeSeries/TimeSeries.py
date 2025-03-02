import requests
import pandas as pd
import numpy as np 
import json
import matplotlib.pyplot as plt
from alpha_vantage.timeseries import TimeSeries
import yfinance as yf
import sqlite3
from datetime import datetime, timedelta

# put the data from data/big4stock/