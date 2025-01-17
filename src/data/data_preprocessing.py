"""
Data preprocessing module for trAIder.

This module handles all data preprocessing tasks including:
- Data cleaning
- Feature engineering
- Normalization
- Time series specific preprocessing
"""

import pandas as pd
import numpy as np
from typing import List, Optional, Union
from datetime import datetime


class DataPreprocessor:
    """Class for preprocessing market data."""
    
    def __init__(self):
        """Initialize the data preprocessor."""
        pass
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean the input data by handling missing values and outliers.
        
        Args:
            df: Input DataFrame with market data
            
        Returns:
            Cleaned DataFrame
        """
        # Remove rows with missing values
        df = df.dropna()
        
        # Remove duplicate timestamps
        df = df.drop_duplicates(subset=['timestamp'])
        
        # Sort by timestamp
        df = df.sort_values('timestamp')
        
        return df
    
    def engineer_features(
        self,
        df: pd.DataFrame,
        features: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Engineer additional features from the raw data.
        
        Args:
            df: Input DataFrame
            features: List of features to engineer (default: None)
            
        Returns:
            DataFrame with additional engineered features
        """
        df = df.copy()
        
        # Calculate returns
        df['returns'] = df['close'].pct_change()
        
        # Calculate log returns
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        
        # Calculate trading volume in base currency
        df['volume_base'] = df['close'] * df['volume']
        
        return df
    
    def normalize_features(
        self,
        df: pd.DataFrame,
        columns: Optional[List[str]] = None,
        method: str = 'minmax'
    ) -> pd.DataFrame:
        """Normalize specified features.
        
        Args:
            df: Input DataFrame
            columns: List of columns to normalize (default: None)
            method: Normalization method ('minmax' or 'zscore')
            
        Returns:
            DataFrame with normalized features
        """
        df = df.copy()
        columns = columns or df.select_dtypes(include=[np.number]).columns
        
        if method == 'minmax':
            for col in columns:
                min_val = df[col].min()
                max_val = df[col].max()
                df[f'{col}_norm'] = (df[col] - min_val) / (max_val - min_val)
        elif method == 'zscore':
            for col in columns:
                mean = df[col].mean()
                std = df[col].std()
                df[f'{col}_norm'] = (df[col] - mean) / std
                
        return df