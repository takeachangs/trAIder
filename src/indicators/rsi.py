"""
Relative Strength Index (RSI) indicator implementation.

This module implements the RSI technical indicator, which measures
momentum by comparing the magnitude of recent gains and losses.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from .base_indicator import BaseIndicator


class RSI(BaseIndicator):
    """RSI indicator implementation."""
    
    def __init__(self, params: Optional[Dict[str, Any]] = None):
        """Initialize RSI indicator.
        
        Args:
            params: Dictionary with parameters:
                - period: RSI calculation period (default: 14)
                - overbought: Overbought threshold (default: 70)
                - oversold: Oversold threshold (default: 30)
        """
        super().__init__(params)
        self.period = self.params.get('period', 14)
        self.overbought = self.params.get('overbought', 70)
        self.oversold = self.params.get('oversold', 30)
    
    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate RSI values.
        
        Args:
            data: DataFrame with market data
            
        Returns:
            DataFrame with RSI values added
        """
        if not self.validate_data(data):
            raise ValueError("Data missing required columns")
        
        df = data.copy()
        
        # Calculate price changes
        df['price_change'] = df['close'].diff()
        
        # Calculate gains and losses
        df['gain'] = df['price_change'].clip(lower=0)
        df['loss'] = -df['price_change'].clip(upper=0)
        
        # Calculate average gains and losses
        avg_gain = df['gain'].rolling(window=self.period).mean()
        avg_loss = df['loss'].rolling(window=self.period).mean()
        
        # Calculate RSI
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on RSI values.
        
        Args:
            data: DataFrame with RSI values
            
        Returns:
            DataFrame with trading signals added
        """
        df = data.copy()
        
        # Generate signals based on overbought/oversold levels
        df['rsi_signal'] = 0  # 0: no signal, 1: buy, -1: sell
        df.loc[df['rsi'] < self.oversold, 'rsi_signal'] = 1
        df.loc[df['rsi'] > self.overbought, 'rsi_signal'] = -1
        
        return df