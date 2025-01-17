"""
Base indicator module for trAIder.

This module provides the base class for all technical indicators.
Each specific indicator should inherit from this base class.
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any, Optional


class BaseIndicator(ABC):
    """Abstract base class for technical indicators."""
    
    def __init__(self, params: Optional[Dict[str, Any]] = None):
        """Initialize the indicator.
        
        Args:
            params: Dictionary of parameters for the indicator
        """
        self.params = params or {}
    
    @abstractmethod
    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate the indicator values.
        
        Args:
            data: DataFrame containing market data
            
        Returns:
            DataFrame with indicator values added
        """
        pass
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on the indicator.
        
        Args:
            data: DataFrame containing market data and indicator values
            
        Returns:
            DataFrame with trading signals added
        """
        pass
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate input data has required columns.
        
        Args:
            data: DataFrame to validate
            
        Returns:
            True if data is valid, False otherwise
        """
        required_columns = {'timestamp', 'open', 'high', 'low', 'close', 'volume'}
        return all(col in data.columns for col in required_columns)