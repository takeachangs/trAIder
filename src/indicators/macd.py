"""
Moving Average Convergence Divergence (MACD) indicator implementation.

This module implements the MACD technical indicator, which shows the relationship
between two moving averages of an asset's price.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from .base_indicator import BaseIndicator


class MACD(BaseIndicator):
    """MACD indicator implementation."""
    
    def __init__(self, params: Optional[Dict[str, Any]] = None):
        """Initialize MACD indicator.
        
        Args:
            params: Dictionary with parameters:
                - fast_period: Fast EMA period (default: 12)
                - slow_period: Slow EMA period (default: 26)
                - signal_period: Signal line period (default: 9)
        """
        super().__init__(params)
        self.fast_period = self.params.get('fast_period', 12)
        self.slow_period = self.params.get('slow_period', 26)
        self.signal_period = self.params.get('signal_period', 9)
    
    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD values.
        
        Args:
            data: DataFrame with market data
            
        Returns:
            DataFrame with MACD values added
        """
        if not self.validate_data(data):
            raise ValueError("Data missing required columns")
        
        df = data.copy()
        
        # Calculate EMAs
        fast_ema = df['close'].ewm(span=self.fast_period, adjust=False).mean()
        slow_ema = df['close'].ewm(span=self.slow_period, adjust=False).mean()
        
        # Calculate MACD line
        df['macd_line'] = fast_ema - slow_ema
        
        # Calculate signal line
        df['signal_line'] = df['macd_line'].ewm(span=self.signal_period, adjust=False).mean()
        
        # Calculate MACD histogram
        df['macd_histogram'] = df['macd_line'] - df['signal_line']
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on MACD values.
        
        Args:
            data: DataFrame with MACD values
            
        Returns:
            DataFrame with trading signals added
        """
        df = data.copy()
        
        # Generate signals based on MACD line crossing signal line
        df['macd_signal'] = 0  # 0: no signal, 1: buy, -1: sell
        df.loc[df['macd_line'] > df['signal_line'], 'macd_signal'] = 1
        df.loc[df['macd_line'] < df['signal_line'], 'macd_signal'] = -1
        
        return df