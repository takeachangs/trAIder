"""
Tests for the technical indicators.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.indicators.rsi import RSI
from src.indicators.macd import MACD
from src.indicators.cusum import CUSUM


@pytest.fixture
def sample_data():
    """Create sample market data for testing."""
    dates = [datetime.now() - timedelta(minutes=i) for i in range(100)]
    
    # Create a simple trend for testing
    prices = np.linspace(100, 200, 100) + np.random.normal(0, 5, 100)
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': prices + 2,
        'low': prices - 2,
        'close': prices,
        'volume': np.random.randint(1000, 2000, 100)
    })
    
    return df.sort_values('timestamp')


def test_rsi_calculation(sample_data):
    """Test RSI indicator calculation."""
    rsi = RSI(params={'period': 14})
    result = rsi.calculate(sample_data)
    
    assert 'rsi' in result.columns
    assert len(result) == len(sample_data)
    assert result['rsi'].min() >= 0
    assert result['rsi'].max() <= 100
    
    # Test signal generation
    signals = rsi.generate_signals(result)
    assert 'rsi_signal' in signals.columns
    assert set(signals['rsi_signal'].unique()).issubset({-1, 0, 1})


def test_macd_calculation(sample_data):
    """Test MACD indicator calculation."""
    macd = MACD(params={
        'fast_period': 12,
        'slow_period': 26,
        'signal_period': 9
    })
    result = macd.calculate(sample_data)
    
    assert 'macd_line' in result.columns
    assert 'signal_line' in result.columns
    assert 'macd_histogram' in result.columns
    assert len(result) == len(sample_data)
    
    # Test signal generation
    signals = macd.generate_signals(result)
    assert 'macd_signal' in signals.columns
    assert set(signals['macd_signal'].unique()).issubset({-1, 0, 1})


def test_cusum_calculation(sample_data):
    """Test CUSUM indicator calculation."""
    cusum = CUSUM(params={
        'threshold': 1.0,
        'drift': 0.0
    })
    result = cusum.calculate(sample_data)
    
    assert 'pos_cusum' in result.columns
    assert 'neg_cusum' in result.columns
    assert len(result) == len(sample_data)
    
    # Test signal generation
    signals = cusum.generate_signals(result)
    assert 'cusum_signal' in signals.columns
    assert set(signals['cusum_signal'].unique()).issubset({-1, 0, 1})


def test_indicator_validation(sample_data):
    """Test indicator data validation."""
    # Create invalid data by removing required columns
    invalid_data = sample_data.drop(['high', 'low'], axis=1)
    
    indicators = [
        RSI(),
        MACD(),
        CUSUM()
    ]
    
    for indicator in indicators:
        with pytest.raises(ValueError):
            indicator.calculate(invalid_data)


def test_indicator_parameters():
    """Test indicator parameter handling."""
    # Test RSI with custom parameters
    rsi = RSI(params={'period': 7, 'overbought': 80, 'oversold': 20})
    assert rsi.period == 7
    assert rsi.overbought == 80
    assert rsi.oversold == 20
    
    # Test MACD with custom parameters
    macd = MACD(params={'fast_period': 8, 'slow_period': 21, 'signal_period': 5})
    assert macd.fast_period == 8
    assert macd.slow_period == 21
    assert macd.signal_period == 5
    
    # Test CUSUM with custom parameters
    cusum = CUSUM(params={'threshold': 2.0, 'drift': 0.1})
    assert cusum.threshold == 2.0
    assert cusum.drift == 0.1