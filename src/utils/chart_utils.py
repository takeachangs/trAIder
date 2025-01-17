"""
Utility functions for chart management and real-time updates.
"""

from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def prepare_chart_data(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare data for charting by ensuring correct format and sorting.
    
    Args:
        df: Raw DataFrame with market data
        
    Returns:
        Processed DataFrame ready for charting
    """
    # Ensure index is datetime
    if not isinstance(df.index, pd.DatetimeIndex):
        if 'timestamp' in df.columns:
            df.set_index('timestamp', inplace=True)
        else:
            raise ValueError("DataFrame must have 'timestamp' column or datetime index")
    
    # Sort by timestamp
    df = df.sort_index()
    
    # Ensure required columns exist
    required_columns = ['open', 'high', 'low', 'close', 'volume']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    return df


def calculate_chart_ranges(data: pd.DataFrame, padding: float = 0.1) -> Dict[str, Dict[str, float]]:
    """Calculate appropriate value ranges for each chart component.
    
    Args:
        data: DataFrame with all required data
        padding: Padding percentage for ranges
        
    Returns:
        Dictionary of range settings for each component
    """
    ranges = {}
    
    # Price chart range
    price_min = data[['low']].min().min()
    price_max = data[['high']].max().max()
    price_padding = (price_max - price_min) * padding
    ranges['price'] = {
        'min': price_min - price_padding,
        'max': price_max + price_padding
    }
    
    # Volume chart range
    volume_max = data['volume'].max()
    ranges['volume'] = {
        'min': 0,
        'max': volume_max * (1 + padding)
    }
    
    # RSI range is fixed
    ranges['rsi'] = {
        'min': 0,
        'max': 100
    }
    
    # MACD range
    if all(col in data.columns for col in ['MACD', 'MACD_signal', 'MACD_hist']):
        macd_min = min(
            data['MACD'].min(),
            data['MACD_signal'].min(),
            data['MACD_hist'].min()
        )
        macd_max = max(
            data['MACD'].max(),
            data['MACD_signal'].max(),
            data['MACD_hist'].max()
        )
        macd_padding = (macd_max - macd_min) * padding
        ranges['macd'] = {
            'min': macd_min - macd_padding,
            'max': macd_max + macd_padding
        }
    
    return ranges


def format_number(value: float, precision: int = 2) -> str:
    """Format number for display with appropriate precision.
    
    Args:
        value: Number to format
        precision: Number of decimal places
        
    Returns:
        Formatted string
    """
    if abs(value) >= 1e6:
        return f"{value/1e6:.{precision}f}M"
    elif abs(value) >= 1e3:
        return f"{value/1e3:.{precision}f}K"
    else:
        return f"{value:.{precision}f}"


def calculate_time_intervals(timeframe: str) -> Dict[str, Any]:
    """Calculate appropriate time intervals for chart display.
    
    Args:
        timeframe: Trading timeframe (e.g., '1m', '5m', '1h', '1d')
        
    Returns:
        Dictionary with time interval settings
    """
    intervals = {}
    
    # Parse timeframe
    value = int(''.join(filter(str.isdigit, timeframe)))
    unit = ''.join(filter(str.isalpha, timeframe))
    
    # Calculate base interval in minutes
    if unit == 'm':
        base_minutes = value
    elif unit == 'h':
        base_minutes = value * 60
    elif unit == 'd':
        base_minutes = value * 1440
    else:
        raise ValueError(f"Unsupported timeframe unit: {unit}")
    
    # Set intervals based on timeframe
    if base_minutes <= 5:  # 1m, 5m
        intervals.update({
            'minor': timedelta(minutes=base_minutes),
            'major': timedelta(hours=1),
            'label': timedelta(hours=4)
        })
    elif base_minutes <= 60:  # 15m, 30m, 1h
        intervals.update({
            'minor': timedelta(hours=1),
            'major': timedelta(hours=4),
            'label': timedelta(hours=12)
        })
    elif base_minutes <= 1440:  # 4h, 1d
        intervals.update({
            'minor': timedelta(days=1),
            'major': timedelta(days=7),
            'label': timedelta(days=30)
        })
    else:  # 1w and above
        intervals.update({
            'minor': timedelta(days=7),
            'major': timedelta(days=30),
            'label': timedelta(days=90)
        })
    
    return intervals


class DataWindow:
    """Class for managing sliding data windows for real-time charts."""
    
    def __init__(self, window_size: int = 100):
        """Initialize data window.
        
        Args:
            window_size: Number of data points to maintain
        """
        self.window_size = window_size
        self.data = pd.DataFrame()
    
    def update(self, new_data: pd.DataFrame) -> pd.DataFrame:
        """Update data window with new data points.
        
        Args:
            new_data: New data to add to window
            
        Returns:
            Updated window of data
        """
        # Concatenate new data
        self.data = pd.concat([self.data, new_data])
        
        # Keep only the latest window_size points
        if len(self.data) > self.window_size:
            self.data = self.data.iloc[-self.window_size:]
        
        return self.data.copy()


class ChartStateManager:
    """Class for managing chart state and coordinating updates."""
    
    def __init__(self, theme: str = 'dark'):
        """Initialize chart state manager.
        
        Args:
            theme: Chart theme ('dark' or 'light')
        """
        self.theme = theme
        self.data_window = DataWindow()
        self.active_indicators = set()
        self.signal_overlay = True
        self.last_update = None
        self.update_counter = 0
    
    def update_state(self, new_data: pd.DataFrame) -> Dict[str, Any]:
        """Update chart state with new data.
        
        Args:
            new_data: New market data
            
        Returns:
            Dictionary with updated state information
        """
        # Update data window
        current_data = self.data_window.update(new_data)
        
        # Calculate ranges
        ranges = calculate_chart_ranges(current_data)
        
        # Update counters
        self.update_counter += len(new_data)
        self.last_update = datetime.now()
        
        return {
            'data': current_data,
            'ranges': ranges,
            'update_count': self.update_counter,
            'last_update': self.last_update
        }
    
    def toggle_indicator(self, indicator: str) -> bool:
        """Toggle indicator visibility.
        
        Args:
            indicator: Name of indicator to toggle
            
        Returns:
            New state of indicator (True if visible)
        """
        if indicator in self.active_indicators:
            self.active_indicators.remove(indicator)
            return False
        else:
            self.active_indicators.add(indicator)
            return True
    
    def toggle_signals(self) -> bool:
        """Toggle signal overlay visibility.
        
        Returns:
            New state of signal overlay
        """
        self.signal_overlay = not self.signal_overlay
        return self.signal_overlay