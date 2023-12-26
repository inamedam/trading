import ccxt
import time

exchange = ccxt.binance({
    'apiKey': 'YOUR_API_KEY',
    'secret': 'YOUR_SECRET',
    'enableRateLimit': True,
})

symbol = 'BTC/USDT'
amount = 0.01
stop_loss = 0.02
take_profit = 0.02

while True:
    # Get the current price of the cryptocurrency
    ticker = exchange.fetch_ticker(symbol)
    price = ticker['last']

    # Buy the cryptocurrency if we haven't already
    if amount > 0:
        order = exchange.create_order(symbol, type='limit', side='buy', amount=amount, price=price)
        print('Bought', amount, 'of', symbol, 'at', price)
        amount = 0

    # Sell the cryptocurrency if the price has gone up or down by the stop loss or take profit amounts
    elif price >= (1 + take_profit) * order['price']:
        order = exchange.create_order(symbol, type='limit', side='sell', amount=order['amount'], price=price)
        print('Sold', order['amount'], 'of', symbol, 'at', price)
        break

    elif price <= (1 - stop_loss) * order['price']:
        order = exchange.create_order(symbol, type='limit', side='sell', amount=order['amount'], price=price)
        print('Sold', order['amount'], 'of', symbol, 'at', price)
        break

    # Wait for a few seconds before checking the price again
    time.sleep(5)