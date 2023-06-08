# !pip install hurst

import numpy as np
import pandas as pd
import yfinance as yf
from hurst import compute_Hc
import matplotlib.pyplot as plt

# Download Nasdaq Composite Index data
nasdaq_data = yf.download('TQQQ', start='2010-01-01', end='2023-06-08')

# Use only the daily closing prices
nasdaq_closing_prices = nasdaq_data['Close']

# Convert the price series into a series of percentage changes (plus 1) to mimic 'random_walk'
nasdaq_changes = nasdaq_closing_prices.pct_change().dropna() + 1

# Compute the Hurst exponent using compute_Hc from the hurst module
H, c, data = compute_Hc(nasdaq_changes, kind='price', simplified=True)

# Plot
f, ax = plt.subplots()
ax.plot(data[0], c*data[0]**H, color="deepskyblue")
ax.scatter(data[0], data[1], color="purple")
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Time interval')
ax.set_ylabel('R/S ratio')
ax.grid(True)
plt.show()

print(f"Hurst Exponent (H): {H:.4f}")

# Wrapper function for compute_Hc that only returns H
def compute_H(series):
    H, _, _ = compute_Hc(series, kind='price', simplified=True)
    return H

# Apply the function to a rolling window of the past 100 trading days
H_values = nasdaq_changes.rolling(100).apply(compute_H)

# Drop missing values (first 99 values will be NaN)
H_values = H_values.dropna()

# Plot the Hurst exponent over time
plt.figure(figsize=(10, 5))
plt.plot(H_values)
plt.xlabel('Date')
plt.ylabel('Hurst Exponent')
plt.title('Hurst Exponent over Time (100 trading day rolling window)')
plt.grid(True)
plt.show()
