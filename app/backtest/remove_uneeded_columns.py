import pandas as pd
filename = 'app/backtest/XRPUSDT.csv'
# Read the DataFrame from CSV
df = pd.read_csv(filename, usecols=['timestamp','open','high','low','close'])

# Perform any operations on the DataFrame if needed
# For example, let's print the first few rows
print("Original DataFrame:")
print(df.head())

# Write the DataFrame back to CSV
df.to_csv(filename, index=False)

print("DataFrame has been written")
