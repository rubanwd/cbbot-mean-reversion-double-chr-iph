# risk_management.py

import pandas as pd
import os
from helpers import Helpers  # Ensure this import is present
from indicators import Indicators

class RiskManagement:
    def __init__(self, atr_period=14, atr_multiplier=1.5, risk_ratio=1.5):
        """
        Initializes the RiskManagement class.

        Args:
            atr_period (int): Period for ATR calculation.
            atr_multiplier (float): Multiplier for ATR to calculate take profit distance.
            risk_ratio (float): Ratio to determine take profit based on ATR.
            stop_loss_percentage (float): Percentage for stop loss calculation.
        """
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier
        self.risk_ratio = risk_ratio
        self.stop_loss_percentage = float(os.getenv("STOP_LOSS_PERCENTAGE", 5.0))
        self.indicators = Indicators()

    def calculate_atr(self, df):
        """
        Calculates the Average True Range (ATR) for the given dataframe.

        Args:
            df (pd.DataFrame): Historical price data.

        Returns:
            float: The latest ATR value.
        """
        high = df['high'].astype(float)
        low = df['low'].astype(float)
        close = df['close'].astype(float)
        df['previous_close'] = close.shift(1)
        df['tr'] = pd.concat([
            high - low,
            (high - df['previous_close']).abs(),
            (low - df['previous_close']).abs()
        ], axis=1).max(axis=1)
        atr = df['tr'].rolling(window=self.atr_period).mean().iloc[-1]
        return atr

    def calculate_dynamic_risk_management(self, df, trend):
        """
        Calculates stop loss and take profit based on fixed percentage for stop loss
        and ATR-based calculation for take profit.

        Args:
            df (pd.DataFrame): Historical price data.
            trend (str): The trend direction ('long' or 'short').

        Returns:
            tuple: (stop_loss, take_profit)
        """
        # Calculate indicators
        rsi, bollinger_upper, bollinger_middle, bollinger_lower, current_price = Helpers.calculate_and_print_indicators(df, self.indicators)
        
        # Calculate ATR for take profit
        atr = self.calculate_atr(df)
        take_profit_distance = self.atr_multiplier * atr * self.risk_ratio

        # Calculate stop loss based on fixed percentage
        stop_loss_distance = (self.stop_loss_percentage / 100) * float(current_price)
        
        if trend == 'long':
            stop_loss = float(current_price) * (1 - self.stop_loss_percentage / 100)
            take_profit = float(current_price) + take_profit_distance
        elif trend == 'short':
            stop_loss = float(current_price) * (1 + self.stop_loss_percentage / 100)
            take_profit = float(current_price) - take_profit_distance
        else:
            raise ValueError("Trend must be either 'long' or 'short'")

        return stop_loss, take_profit
