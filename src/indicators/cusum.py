"""
Cumulative Sum (CUSUM) filter implementation.

This module implements the CUSUM filter, which is used to detect changes
in the mean of a process and can be used for trend detection.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from .base_indicator import BaseIndicator


class CUSUM(BaseIndicator):
    """CUSUM filter implementation."""
    
    def __init__(self, params: Optional[Dict[str, Any]] = None):
        """Initialize CUSUM filter.
        
        Args:
            params: Dictionary with parameters:
                - threshold: Detection threshold (default: 1.0)
                - drift: Drift parameter (default: 0.0)
        """
        super().__init__(params)
        self.threshold = self.params.get('threshold', 1.0)
        self.drift = self.params.get('drift', 0.0)
    
    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate CUSUM values.
        
        Args:
            data: DataFrame with market data
            
        Returns:
            DataFrame with CUSUM values added
        """
        if not self.validate_data(data):
            raise ValueError("Data missing required columns")
        
        df = data.copy()
        
        # Calculate returns
        returns = df['close'].pct_change()
        
        # Initialize CUSUM arrays
        pos_cusum = np.zeros(len(returns))
        neg_cusum = np.zeros(len(returns))
        
        # Calculate CUSUM values
        for i in range(1, len(returns)):
            pos_cusum[i] = max(0, pos_cusum[i-1] + returns[i] - self.drift)
            neg_cusum[i] = min(0, neg_cusum[i-1] + returns[i] + self.drift)
        
        df['pos_cusum'] = pos_cusum
        df['neg_cusum'] = neg_cusum
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on CUSUM values.
        
        Args:
            data: DataFrame with CUSUM values
            
        Returns:
            DataFrame with trading signals added
        """
        df = data.copy()
        
        # Generate signals based on threshold crossings
        df['cusum_signal'] = 0  # 0: no signal, 1: buy, -1: sell
        df.loc[df['pos_cusum'] > self.threshold, 'cusum_signal'] = 1
        df.loc[df['neg_cusum'] < -self.threshold, 'cusum_signal'] = -1
        
        return df