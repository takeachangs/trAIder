"""
Helper utilities for trAIder.

This module provides various utility functions used throughout the project.
"""

import logging
from datetime import datetime, timezone
from typing import Union, Optional
import pandas as pd


def setup_logging(level: int = logging.INFO) -> None:
    """Set up logging configuration.
    
    Args:
        level: Logging level (default: logging.INFO)
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def convert_timestamp(
    timestamp: Union[str, int, float, datetime],
    to_datetime: bool = True
) -> Union[datetime, int]:
    """Convert between timestamp formats.
    
    Args:
        timestamp: Input timestamp
        to_datetime: Convert to datetime if True, else to unix timestamp
        
    Returns:
        Converted timestamp
    """
    if isinstance(timestamp, str):
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    elif isinstance(timestamp, (int, float)):
        dt = datetime.fromtimestamp(timestamp / 1000 if timestamp > 1e11 else timestamp, tz=timezone.utc)
    elif isinstance(timestamp, datetime):
        dt = timestamp
    else:
        raise ValueError(f"Unsupported timestamp format: {type(timestamp)}")
    
    return dt if to_datetime else int(dt.timestamp() * 1000)


def format_number(
    number: float,
    decimals: Optional[int] = None,
    format_type: str = 'standard'
) -> str:
    """Format numbers for display.
    
    Args:
        number: Number to format
        decimals: Number of decimal places
        format_type: Format type ('standard', 'percentage', 'currency')
        
    Returns:
        Formatted number string
    """
    if format_type == 'percentage':
        return f"{number:.{decimals or 2}f}%"
    elif format_type == 'currency':
        return f"${number:,.{decimals or 2}f}"
    else:
        if decimals is not None:
            return f"{number:,.{decimals}f}"
        return f"{number:,}"


class DataFrameUtils:
    """Utility functions for DataFrame operations."""
    
    @staticmethod
    def ensure_datetime_index(df: pd.DataFrame, column: str = 'timestamp') -> pd.DataFrame:
        """Ensure DataFrame has a datetime index.
        
        Args:
            df: Input DataFrame
            column: Column to use as index
            
        Returns:
            DataFrame with datetime index
        """
        df = df.copy()
        if column in df.columns:
            df[column] = pd.to_datetime(df[column])
            df.set_index(column, inplace=True)
        return df
    
    @staticmethod
    def resample_ohlcv(
        df: pd.DataFrame,
        interval: str,
        price_column: str = 'close'
    ) -> pd.DataFrame:
        """Resample OHLCV data to a different interval.
        
        Args:
            df: Input DataFrame with OHLCV data
            interval: Target interval (e.g., '1min', '5min', '1h')
            price_column: Column name for price data
            
        Returns:
            Resampled DataFrame
        """
        df = df.copy()
        
        # Ensure we have a datetime index
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("DataFrame must have a datetime index")
        
        resampled = pd.DataFrame()
        resampled['open'] = df[price_column].resample(interval).first()
        resampled['high'] = df[price_column].resample(interval).max()
        resampled['low'] = df[price_column].resample(interval).min()
        resampled['close'] = df[price_column].resample(interval).last()
        resampled['volume'] = df['volume'].resample(interval).sum()
        
        return resampled.dropna()