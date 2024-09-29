import schedule
import time
import logging
from data_fetcher import DataFetcher
from indicators import Indicators
from strategies import Strategies
from risk_management import RiskManagement
from dotenv import load_dotenv
import os
import pandas as pd
from bybit_demo_session import BybitDemoSession
from helpers import Helpers  # Import the Helpers module
from indicators import Indicators

class TradingBot:
    def __init__(self):
        load_dotenv()

        self.api_key = os.getenv("BYBIT_API_KEY")
        self.api_secret = os.getenv("BYBIT_API_SECRET") 

        if not self.api_key or not self.api_secret:
            raise ValueError("API keys not found. Please set BYBIT_API_KEY and BYBIT_API_SECRET in your .env file.")

        self.data_fetcher = BybitDemoSession(self.api_key, self.api_secret)

        self.strategy = Strategies()
        self.indicators = Indicators()
        self.risk_management = RiskManagement()
        self.symbol = os.getenv("TRADING_SYMBOL", 'BTCUSDT')
        self.quantity = float(os.getenv("TRADE_QUANTITY", 0.03))

        # Load trading parameters
        self.interval = os.getenv("TRADING_INTERVAL", '1')
        self.limit = int(os.getenv("TRADING_LIMIT", 100))
        self.leverage = int(os.getenv("LEVERAGE", 10))

        # Set up logging
        logging.basicConfig(filename='trading_bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
    def job(self):

        print("--------------------")

        is_open_positions = self.data_fetcher.get_open_positions(self.symbol)
        if is_open_positions:
            print("There is already an open position. A new order will not be placed.")
            return
        

        is_open_orders = self.data_fetcher.get_open_orders(self.symbol)
        if is_open_orders:
            print("There is an open limit order. A new order will not be placed.")
            return
        
        get_historical_data = self.data_fetcher.get_historical_data(self.symbol, self.interval, self.limit)
        if get_historical_data is None:
            print("Failed to retrieve historical data.")
            return

        df = self.strategy.prepare_dataframe(get_historical_data)
        
        trend = self.strategy.mean_reversion_strategy(df)
        if trend:

            last_closed_position = self.data_fetcher.get_last_closed_position(self.symbol)
            if last_closed_position:
                last_closed_time = int(last_closed_position['updatedTime']) / 1000
                current_time = time.time()
                time_since_last_close = current_time - last_closed_time
                print(f"Time since last closed position: {int(time_since_last_close)} seconds")
                if time_since_last_close < 120:
                    print("The last closed position was less than 1 minute ago. A new order will not be placed.")
                    return
                
            
            stop_loss, take_profit = self.risk_management.calculate_dynamic_risk_management(df, trend)

            print(f"Trend: {trend.upper()}")
            print(f"Stop Loss: {stop_loss:.2f}")
            print(f"Take Profit: {take_profit:.2f}")

            side = 'Buy' if trend == 'long' else 'Sell'
            print(f"Order side: {side}")

            rsi, bollinger_upper, bollinger_middle, bollinger_lower, current_price = Helpers.calculate_and_print_indicators(df, self.indicators)

            order_result = self.data_fetcher.place_order(
                symbol=self.symbol,
                side=side,
                qty=self.quantity,
                current_price=current_price,
                leverage=self.leverage,
                stop_loss=stop_loss,
                take_profit=take_profit
            )

            if order_result:
                print(f"Order successfully placed: {order_result}")
            else:
                print("Failed to place order.")
        else:
            print("No suitable signals for position opening.")

    def run(self):
        self.job()
        schedule.every(2).seconds.do(self.job)
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    bot = TradingBot()
    bot.run()
