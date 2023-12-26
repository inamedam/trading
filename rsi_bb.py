import ccxt
import talib
import numpy as np
import time

# Binance API keys
exchange = ccxt.binance({
    'apiKey': 'YOUR_API_KEY',
    'secret': 'YOUR_SECRET',
    'enableRateLimit': True,
})

# Symbol and timeframe
symbol = 'BTC/USDT'
timeframe = '1h'

# RSI and BB parameters
rsi_period = 14
bb_period = 20
bb_dev = 2

# Initial order parameters
initial_order_size = 0.01
initial_stop_loss = 0.02
initial_take_profit = 0.02

# Variables to track open positions and order parameters
position_open = False
position_type = None
position_size = 0
stop_loss = initial_stop_loss
take_profit = initial_take_profit

while True:
    # Get historical prices for RSI and BB calculation
    prices = exchange.fetch_ohlcv(symbol, timeframe)
    close = np.array([float(p[4]) for p in prices])

    # Calculate RSI and BB
    rsi = talib.RSI(close, timeperiod=rsi_period)
    upper, middle, lower = talib.BBANDS(close, timeperiod=bb_period, nbdevup=bb_dev, nbdevdn=bb_dev, matype=0)

    # Get the current price of the cryptocurrency
    ticker = exchange.fetch_ticker(symbol)
    price = ticker['last']

    # Buy signal: RSI below 30 and price below lower Bollinger Band
    if rsi[-1] < 30 and price < lower[-1]:
        # Buy the cryptocurrency
        order = exchange.create_order(symbol, type='limit', side='buy', amount=initial_order_size, price=price)
        print('Bought', initial_order_size, 'of', symbol, 'at', price)
        position_open = True
        position_type = 'long'
        position_size = initial_order_size

    # Sell signal: RSI above 70 and price above upper Bollinger Band
    elif rsi[-1] > 70 and price > upper[-1]:
        # Sell the cryptocurrency
        order = exchange.create_order(symbol, type='limit', side='sell', amount=position_size, price=price)
        print('Sold', position_size, 'of', symbol, 'at', price)
        position_open = False
        position_type = None
        position_size = 0

    # Update stop-loss and take-profit levels
    if position_open:
        if position_type == 'long':
            stop_loss_price = order['price'] * (1 - stop_loss)
            take_profit_price = order['price'] * (1 + take_profit)
            if price < stop_loss_price:
                # Sell the cryptocurrency with stop-loss
                order = exchange.create_order(symbol, type='limit', side='sell', amount=position_size, price=price)
                print('Sold', position_size, 'of', symbol, 'at', price, 'with stop-loss')
                position_open = False
                position_type = None
                position_size = 0
            elif price > take_profit_price:
                # Sell the cryptocurrency with take-profit
                order = exchange.create_order(symbol, type='limit', side='sell', amount=position_size, price=price)
                print('Sold', position_size, 'of', symbol, 'at', price, 'with take-profit')
