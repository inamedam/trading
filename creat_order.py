import ccxt

exchange = ccxt.binance({
    'apiKey': 'YOUR_API_KEY',
    'secret': 'YOUR_SECRET',
    'enableRateLimit': True,
})

symbol = 'BTC/USDT'
amount = 0.01

while True:
    ticker = exchange.fetch_ticker(symbol)
    price = ticker['last']

    if price < 50000:
        order = exchange.create_order(symbol, type='limit', side='buy', amount=amount, price=price)
        print('Bought', amount, 'of', symbol, 'at', price)

    elif price > 55000:
        order = exchange.create_order(symbol, type='limit', side='sell', amount=amount, price=price)
        print('Sold', amount, 'of', symbol, 'at', price)
