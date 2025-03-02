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

# Extract '10-K' data for each financial variable
def extract_10K_data(df_json, key):
    extracted_data = []
    for name in df_json[key]:
        for i in range(len(name)):
            if name[i]['form'] == '10-K':
                extracted_data.append([name[i]['fy'], name[i]['val']])
    return extracted_data

# Extract data
Revenue_10K = extract_10K_data(df_json, 'Revenue')
Netincome_10K = extract_10K_data(df_json, 'NetIncome')
OperatingIncome_10K = extract_10K_data(df_json, 'OperatingIncome')
PropertyPlantandEquipment_10K = extract_10K_data(df_json, 'PropertyPlantandEquipment')
OperatingLeaseLiability_10K = extract_10K_data(df_json, 'OperatingLeaseLiability')
CapitalExpenditures_10K = extract_10K_data(df_json, 'CapitalExpenditures')
TotalAssets_10K = extract_10K_data(df_json, 'TotalAssets')

# Combine all extracted data based on matching fiscal years (fy)
combined_data = []
for rev in Revenue_10K:
    fy = rev[0]  # Fiscal year
    revenue_val = rev[1]
    
    land_val = next((x[1] for x in Land_10K if x[0] == fy), None)
    netincome_val = next((x[1] for x in NetIncome_10K if x[0] == fy), None)
    operatingincome_val = next((x[1] for x in OperatingIncome_10K if x[0] == fy), None)
    ppe_val = next((x[1] for x in PropertyPlantandEquipment_10K if x[0] == fy), None)
    lease_val = next((x[1] for x in OperatingLeaseLiability_10K if x[0] == fy), None)
    capex_val = next((x[1] for x in CapitalExpenditures_10K if x[0] == fy), None)
    assets_val = next((x[1] for x in TotalAssets_10K if x[0] == fy), None)
    
    if land_val is not None:
        combined_data.append([fy, land_val, netincome_val, operatingincome_val, 
                              ppe_val, lease_val, capex_val, assets_val])

# Define a function to create scatter plots
def plot_scatter(x, y, x_label, y_label, title):
    plt.figure(figsize=(8, 5))
    plt.scatter(x, y, alpha=0.7, edgecolors='k')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.grid(True)
    plt.show()

# Extract Land values and other financial metrics for plotting
land_vals = [row[1] for row in combined_data]  # Land is at index 1

# Dictionary to store each variable separately for plotting
plot_data = {
    "Revenue": [row[2] for row in combined_data],
    "Net Income": [row[2] for row in combined_data],  
    "Operating Income": [row[3] for row in combined_data],  
    "Property, Plant & Equipment": [row[4] for row in combined_data],  
    "Operating Lease Liability": [row[5] for row in combined_data],  
    "Capital Expenditures": [row[6] for row in combined_data],  
    "Total Assets": [row[7] for row in combined_data]  
}

# Generate scatter plots
for key, y_vals in plot_data.items():
    plot_scatter(land_vals, y_vals, "Land Value", key, f"Land vs {key}")


'''     
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

NetIncome_10K = []
for name in df_json['Netincome']:
    for i in range(len(name)):
        if name[i]['form'] == '10-K':
            Netincome_10K.append([name[i]['fy'], name[i]['val']])

OperatingIncome_10K = []
for name in df_json['OperatingIncome']:
    for i in range(len(name)):
        if name[i]['form'] == '10-K':
            OperatingIncome_10K.append([name[i]['fy'], name[i]['val']])

PropertyPlantandEquipment_10K = []
for name in df_json['PropertyPlantandEquipment']:
    for i in range(len(name)):
        if name[i]['form'] == '10-K':
            PropertyPlantandEquipment_10K.append([name[i]['fy'], name[i]['val']])

OperatingLeaseLiability_10K = []
for name in df_json['OperatingLeaseLiability']:
    for i in range(len(name)):
        if name[i]['form'] == '10-K':
            OperatingLeaseLiability_10K.append([name[i]['fy'], name[i]['val']])

CapitalExpenditures_10K = []
for name in df_json['CapitalExpenditures']:
    for i in range(len(name)):
        if name[i]['form'] == '10-K':
            CapitalExpenditures_10K.append([name[i]['fy'], name[i]['val']])

TotalAssets_10K = []
for name in df_json['TotalAssets']:
    for i in range(len(name)):
        if name[i]['form'] == '10-K':
            TotalAssets_10K.append([name[i]['fy'], name[i]['val']])

combined_data = []
for i in range(len(Revenue_10K)):
    for j in range(len(Land_10K)):
        if Revenue_10K[i][0] == Land_10K[j][0]:
            combined_data.append([Revenue_10K[i][0], Revenue_10K[i][1], Land_10K[j][1]])
        
print(combined_data)


year = [data[0] for data in combined_data]
x = [data[1] for data in combined_data]
y = [data[2] for data in combined_data]

plt.scatter(x, y, c=year)
plt.xlabel('Revenue')
plt.ylabel('Land')
plt.title('Scatter Plot')
plt.colorbar(label='Year')
'''


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
