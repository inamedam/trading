from binance.client import Client
import time
import pandas as pd
import numpy as np
import ta
import config

# Initialize Binance client
client = Client(config.api_key, config.api_secret)

symbol = 'BTCUSDT'  # Replace with the desired trading symbol

# Create Binance client

# Function to fetch live data
def get_live_data(symbol):
    klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE)
    df = pd.DataFrame(klines, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df['Close'] = df['Close'].astype(float)
    return df

# Function to calculate trading signals
def generate_signals(df):
    df['qqe'] = ta.momentum.qqe(df['Close'], length=3, threshold=20)  # QQE with length=3 and threshold=20

    # Volume Flow Indicator (VFI) by LazyBear
    df['vfi'] = ta.volume.volume_flow_indicator(df['Close'], df['Volume'], length=100, vmax=1.5, signal_length=20)
    
    df['stochrsi_k'] = ta.momentum.stochrsi_k(df['Close'])
    df['stochrsi_d'] = ta.momentum.stochrsi_d(df['Close'])

    for i in (8, 14, 50):
        df['EMA_' + str(i)] = ta.trend.ema_indicator(df['Close'], window=i)

    df['High'] = pd.to_numeric(df['High'])
    df['Low'] = pd.to_numeric(df['Low'])
    df['Close'] = pd.to_numeric(df['Close'])

    df['atr'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'])
    df.dropna(inplace=True)

    def check_cross(row):
        return row['stochrsi_k'] > row['stochrsi_d']

    df['cross'] = df.apply(check_cross, axis=1)

    df['TP'] = df['Close'] + (df['atr'] * 2)
    df['SL'] = df['Close'] - (df['atr'] * 3)

    df['Buysignal'] = np.where(
        (df['Close'] > df['EMA_50']) &  # Condition 1
        (df['Close'] > df['High'].shift(1)) &  # Condition 1.5
        (df['vfi'] < df['vfi'].shift(1)) & (df['vfi'] > 0) & (df['vfi'].shift(1) > 0) &  # Condition 1.5
        (df['qqe'] > 20),  # Condition 2
        1, 0
    )

    df['Sellsignal'] = np.where(
        (df['Close'] < df['EMA_50']) &  # Condition 1
        (df['Close'] < df['Low'].shift(1)) &  # Condition 1.5
        (df['vfi'] > df['vfi'].shift(1)) & (df['vfi'] < 0) & (df['vfi'].shift(1) < 0) &  # Condition 1.5
        (df['qqe'] < 0),  # Condition 2
        1, 0
    )

    selldates = []
    outcome = []

    for i in range(len(df)):
        if df['Buysignal'].iloc[i]:
            k = 1
            SL = df['SL'].iloc[i]
            TP = df['TP'].iloc[i]
            in_position = True
            while in_position:
                looping_close = df['Close'].iloc[i + k]
                if looping_close >= TP:
                    selldates.append(df.iloc[i + k].name)
                    outcome.append('TP')
                    in_position = False
                elif looping_close <= SL:
                    selldates.append(df.iloc[i + k].name)
                    outcome.append('SL')
                    in_position = False
                elif df['qqe'].iloc[i + k] < 0:  # Close the position if QQE threshold goes below 0
                    selldates.append(df.iloc[i + k].name)
                    outcome.append('QQE_below_0')
                    in_position = False
                k += 1

    df.loc[selldates, 'Sellsignal'] = 1
    df.loc[selldates, 'outcome'] = outcome
    df['Sellsignal'] = df['Sellsignal'].fillna(0).astype(int)

def execute_trade(symbol, side, quantity):
    try:
        order = client.create_order(
                symbol=symbol,
                side=side,
                type=Client.ORDER_TYPE_MARKET,
                quantity=quantity
            )
        print(f"Successfully executed {side} order: {order}")
    except Exception as e:
        print(f"Failed to execute {side} order: {e}")

# Main loop
while True:
    # Fetch live data
    live_data = get_live_data(symbol)

        # Check if data is available
    if not live_data.empty:
            # Generate trading signals
        signals = generate_signals(live_data)

            # Check if a buy signal is generated
        if signals['Buysignal'].iloc[-1] == 1:
                # Buy the asset
            execute_trade(symbol, side=Client.SIDE_BUY, quantity=30)

                # Set take profit and stop loss levels
            take_profit = signals['TP'].iloc[-1]
            stop_loss = signals['SL'].iloc[-1]

                # Monitor the position
            while True:
                    # Fetch updated live data
                live_data = get_live_data(symbol)

                    # Check if the current price reaches the take profit level
                if live_data['Close'].iloc[-1] >= take_profit:
                        # Sell the asset and exit the position
                    execute_trade(symbol, side=Client.SIDE_SELL, quantity=30)
                    break

                    # Check if the current price reaches the stop loss level
                elif live_data['Close'].iloc[-1] <= stop_loss:
                        # Sell the asset and exit the position
                    execute_trade(symbol, side=Client.SIDE_SELL, quantity=30)
                    break

                    # Wait for the next data update
                time.sleep(60)  # Wait for 1 minute before checking again
