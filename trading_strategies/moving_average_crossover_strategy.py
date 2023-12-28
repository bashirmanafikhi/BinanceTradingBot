import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def moving_average_crossover_strategy(data, short_window, long_window):
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0

    # Create short simple moving average
    signals['short_avg'] = data['close'].rolling(window=short_window, min_periods=1, center=False).mean()

    # Create long simple moving average
    signals['long_avg'] = data['close'].rolling(window=long_window, min_periods=1, center=False).mean()

    # Create signals
    signals['signal'][short_window:] = np.where(signals['short_avg'][short_window:] > signals['long_avg'][short_window:], 1.0, 0.0)

    # Generate trading orders
    signals['positions'] = signals['signal'].diff()

    return signals

def exponential_moving_average_crossover_strategy(data, short_window, long_window):
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0

    # Create short exponential moving average
    signals['short_avg'] = data['close'].ewm(span=short_window, adjust=False).mean()

    # Create long exponential moving average
    signals['long_avg'] = data['close'].ewm(span=long_window, adjust=False).mean()

    # Create signals
    signals['signal'][short_window:] = np.where(signals['short_avg'][short_window:] > signals['long_avg'][short_window:], 1.0, 0.0)

    # Generate trading orders
    signals['positions'] = signals['signal'].diff()

    return signals

def plot_signals(data, signals):
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot Close Price
    ax1.plot(data.index, data['close'], label='Close Price', linewidth=2)

    # Plot Buy signals
    ax1.plot(signals.loc[signals.positions == 1.0].index,
             data['close'][signals.positions == 1.0],
             '^', markersize=10, color='g', label='Buy Signal')

    # Plot Sell signals
    ax1.plot(signals.loc[signals.positions == -1.0].index,
             data['close'][signals.positions == -1.0],
             'v', markersize=10, color='r', label='Sell Signal')

    ax1.set_xlabel('Date')
    ax1.set_ylabel('Close Price', color='black')
    ax1.tick_params('y', colors='black')
    ax1.legend(loc='upper left')

    # Create a secondary y-axis for the moving averages
    ax2 = ax1.twinx()
    ax2.plot(signals['short_avg'], label='Short-Term MA', linestyle='--', color='blue')
    ax2.plot(signals['long_avg'], label='Long-Term MA', linestyle='--', color='orange')
    ax2.set_ylabel('Moving Averages', color='black')
    ax2.tick_params('y', colors='black')
    ax2.legend(loc='upper right')

    ax1.set_title('Moving Average Crossover Strategy')
    plt.show()
