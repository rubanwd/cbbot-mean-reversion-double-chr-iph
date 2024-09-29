# strategy.py

import pandas as pd
from helpers import Helpers
from indicators import Indicators

class Strategies:
    def __init__(self):
        self.indicators = Indicators()
        self.high_rsi = 70
        self.low_rsi = 30

    def prepare_dataframe(self, historical_data):
        df = pd.DataFrame(historical_data)
        df.columns = ["timestamp", "open", "high", "low", "close", "volume", "turnover"]
        df['close'] = df['close'].astype(float)
        df.sort_values('timestamp', inplace=True)
        return df

    def mean_reversion_strategy(self, df):
        rsi, bollinger_upper, bollinger_middle, bollinger_lower, current_price = Helpers.calculate_and_print_indicators(df, self.indicators)

        # Print the indicator values
        print(f"RSI: {rsi:.2f}")
        print(f"Bollinger Upper: {bollinger_upper:.2f}")
        print(f"Bollinger Middle: {bollinger_middle:.2f}")
        print(f"Bollinger Lower: {bollinger_lower:.2f}")
        print(f"Current Price: {current_price:.2f}")

        # Check for overbought (short) or oversold (long) conditions

        # if current_price + 300 >= bollinger_upper:
        #     return 'short'
        # elif current_price - 300 <= bollinger_lower:
        #     return 'long'
        # return None

        # if rsi > self.high_rsi or (current_price - 170) >= bollinger_upper:
        #     return 'short'
        # elif rsi < self.low_rsi or (current_price + 170) <= bollinger_lower:
        #     return 'long'
        # return None
    
        if rsi > self.high_rsi or current_price >= bollinger_upper:
            return 'short'
        elif rsi < self.low_rsi or current_price <= bollinger_lower:
            return 'long'
        return None
    
        # if rsi > 50:
        #     return 'long'
        # elif rsi < 50:
        #     return 'short'
        # return None

