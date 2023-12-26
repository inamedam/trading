#probleme of calcul of price voire excel
import time
from binance.client import Client
from binance.enums import *
import config


# Declare variables Q quantity and P prices and W total win rate and x win rate each operation
quantity = 100
current_quantity = 0
price = 0
current_profit = 0
incrementation_profit = 0
incrementation_leverage = 1  
#define classe variable all


# Initialize the Binance client
client = Client(config.api_key, config.api_secret)

# Set the symbol and quantity
symbol = "ADAUSDT"
quantity = 100

# Get the latest price for the symbol
ticker = client.futures_symbol_ticker(symbol=symbol)
price = float(ticker['price'])


# lancer order de buy (initial)
# Place the initial buy order with leverage set to 1
leverage = 1
buy_order = client.futures_create_order( symbol=symbol, side=SIDE_BUY, type=ORDER_TYPE_MARKET, quantity=quantity, leverage=leverage)

# Keep track of the current order and the current quantity
current_order = buy_order
current_quantity = quantity

# Keep track of the initial investment
initial_investment = quantity * price



# Loop over a range of values for W
while current_profit <= 100:

    #read price at this moment read(P)
    # Wait for 1 second before checking the price again
    time.sleep(1)
    
     # Calculate the stop loss and take profit prices
    stop_loss_price = price - (price * 0.01)
    take_profit_price = price + (price * 0.01)
    
    # Get the latest price for the symbol
    ticker = client.futures_symbol_ticker(symbol=symbol)
    price = float(ticker['price'])
    
    # Calculate the current profit
    current_profit = ((current_quantity * price) - initial_investment) / initial_investment * 100


    if price <= stop_loss_price:
        # function sell
        # Close the current order and start a new order with double the quantity and leverage
        client.futures_cancel_order(
            symbol=symbol,
            orderId=current_order['orderId'])
        sell_order = client.futures_create_order(
            symbol=symbol,
            side=SIDE_SELL,
            type=ORDER_TYPE_MARKET,
            quantity=quantity,
            leverage=leverage)
        
        incrementation_profit = -1 * incrementation_leverage  # multiply of Q w incrementer x
        incrementation_leverage = 2 * incrementation_leverage
        leverage = incrementation_leverage
        price = stop_loss_price
        #quantity = incrementation_leverage * quantity #boucle incrementer 2
        print("Q_initial", quantity)
        print("loss", incrementation_profit)

        # function buy (Q_initial)
        new_order = client.futures_create_order(
            symbol=symbol,
            side=SIDE_BUY,
            type=ORDER_TYPE_MARKET,
            quantity=quantity,
            leverage=leverage)
       
        #new order    
        current_order = new_order
        
        #initialiser quantite a 100
        quantity = 100
    
    
    elif price >= take_profit_price:
    
        # Close the current order and take profit
        client.futures_cancel_order(
            symbol=symbol,
            orderId=current_order['orderId'])
        sell_order = client.futures_create_order(
            symbol=symbol,
            side=SIDE_SELL,
            type=ORDER_TYPE_MARKET,
            quantity=quantity,
            leverage=leverage)


        incrementation_profit = 1 * incrementation_leverage
        price = take_profit_price  #P choose read P instead of P_initial0
        quantity = 100
        incrementation_leverage = 1
        leverage = incrementation_leverage
        
        # function buy (Q_initial)
        new_order = client.futures_create_order(
            symbol=symbol,
            side=SIDE_BUY,
            type=ORDER_TYPE_MARKET,
            quantity=quantity,
            leverage=leverage)
       
        #new order    
        current_order = new_order

        print("Q_initial", quantity)
        print("win", incrementation_profit)
        
        
        
    current_profit = current_profit + incrementation_profit
    incrementation_profit = 0
    print("win rate", current_profit)


# Close the current order and take profit
client.futures_cancel_order( symbol=symbol, orderId=current_order['orderId'])
sell_order = client.futures_create_order( symbol=symbol, side=SIDE_SELL, type=ORDER_TYPE_MARKET, quantity=quantity, leverage=leverage)

