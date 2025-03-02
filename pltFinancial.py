import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Read the CSV file
df = pd.read_csv('MCD_Combined.csv')

# Convert columns to numeric, coercing errors to NaN
numeric_columns = ['Net_Income', 'Operating_Income', 'Revenue', 'Land', 'PropertyPlantAndEquipment', 'TotalAssets']
for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Drop rows with NaN values
df = df.dropna()

# Create a pair plot
plt.figure(figsize=(20, 20))
sns.pairplot(df[numeric_columns], height=2.5, aspect=1.2, plot_kws={'alpha': 0.6})
plt.suptitle("McDonald's (MCD) Financial Parameters Pair Plot", y=1.02, fontsize=16)
plt.tight_layout()
plt.savefig('MCD_pairplot.pdf')
plt.close()

# Create a correlation heatmap
plt.figure(figsize=(12, 10))
correlation_matrix = df[numeric_columns].corr()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1, center=0)
plt.title("Correlation Heatmap of McDonald's (MCD) Financial Parameters", fontsize=16)
plt.tight_layout()
plt.savefig('MCD_correlation_heatmap.pdf')
plt.close()

print("Plots have been saved as 'MCD_pairplot.pdf' and 'MCD_correlation_heatmap.pdf'")
