import ccxt
import time


exchange = ccxt.binance({
    'apiKey': 'your_api_key',
    'secret': 'your_secret_key'
})


symbol = 'BTC/USDT' # The trading symbol
grid_size = 10 # The number of levels in the grid
distance = 0.02 # The distance between each level
base_price = exchange.fetch_ticker(symbol)['last'] # The current market price
buy_prices = [base_price - (i * distance * base_price) for i in range(grid_size)] # The prices to place buy orders
sell_prices = [base_price + (i * distance * base_price) for i in range(grid_size)] # The prices to place sell orders
stop_loss = 0.05 # The stop loss percentage
take_profit = 0.05 # The take profit percentage


for i in range(grid_size):
    buy_order = exchange.create_limit_buy_order(symbol, 1, buy_prices[i])
    sell_order = exchange.create_limit_sell_order(symbol, 1, sell_prices[i])
    print(f'Buy order placed at {buy_prices[i]}')
    print(f'Sell order placed at {sell_prices[i]}')


while True:
    time.sleep(30) # Wait for 30 seconds
    current_price = exchange.fetch_ticker(symbol)['last'] # Get the current market price
    for i in range(grid_size):
        buy_order = exchange.fetch_order(buy_order['id'])
        sell_order = exchange.fetch_order(sell_order['id'])
        if current_price >= sell_order['price'] * (1 + take_profit):
            # If the price has gone up by 5%, sell the position
            exchange.create_market_sell_order(symbol, sell_order['filled'], {'stopPrice': sell_order['price'] * (1 - stop_loss)})
            # Place a new buy order at the current market price minus 2%
            buy_order = exchange.create_limit_buy_order(symbol, 1, current_price * (1 - distance))
            print(f'Sell order filled at {sell_order['price']}. New buy order placed at {buy_order['price']}.')
        elif current_price <= buy_order['price'] * (1 - take_profit):
            # If the price has gone down by 5%, buy the position
            exchange.create_market_buy_order(symbol, buy_order['filled'], {'stopPrice': buy_order['price'] * (1 + stop_loss)})
            # Place a new sell order at the current market price plus 2%
            sell_order = exchange.create_limit_sell_order(symbol, 1, current_price * (1 + distance))
            print(f'Buy order filled at {buy_order['price']}. New sell order placed at {sell_order['price']}.')
