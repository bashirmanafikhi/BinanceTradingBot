import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from helpers.settings.constants import ACTION_BUY, ACTION_SELL

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

def add_moving_average(signals, short_window, long_window):

    signals.ta.ema(100, append=True)
    signals.ta.ema(length=short_window, append=True)
    signals.ta.ema(length=long_window, append=True)

    return signals

def plot_signals(signals):
    # Apply the function to fill the 'positions' column
    signals['positions'] = signals['trades'].apply(map_action_to_position)

    signals = add_moving_average(signals, 9, 21)
    
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot Close Price
    ax1.plot(signals.index, signals['close'], label='Close Price', linewidth=2)
    
    # Plot Buy signals
    ax1.plot(signals.loc[signals.positions == 1.0].index,
             signals[signals.positions == 1.0]['close'],
             '^', markersize=10, color='g', label='Buy Signal')

    # Plot Sell signals
    ax1.plot(signals.loc[signals.positions == -1.0].index,
             signals[signals.positions == -1.0]['close'],
             'v', markersize=10, color='r', label='Sell Signal')

    ax1.set_xlabel('Date')
    ax1.set_ylabel('Close Price', color='black')
    ax1.tick_params('y', colors='black')
    ax1.legend(loc='upper left')

    # Create a secondary y-axis for the moving averages
    ax2 = ax1.twinx()
    ax2.plot(signals['EMA_9'], label='EMA 9', linestyle='--', color='blue')
    ax2.plot(signals['EMA_21'], label='EMA 21', linestyle='--', color='orange')
    ax2.plot(signals['EMA_100'], label='EMA 100', linestyle='--', color='red')
    ax2.set_ylabel('Moving Averages', color='black')
    ax2.tick_params('y', colors='black')
    ax2.legend(loc='upper right')

    ax1.set_title('Moving Average Crossover Strategy')
    plt.show()
    plt.show()

    
# Define a function to map 'ACTION_BUY' to 1, 'ACTION_SELL' to -1, and others to 0
def map_action_to_position(trade_list):
    if trade_list and len(trade_list) > 0:
        first_trade = trade_list[0]
        if first_trade['action'] == ACTION_BUY:
            return 1
        elif first_trade['action'] == ACTION_SELL:
            return -1
    return 0