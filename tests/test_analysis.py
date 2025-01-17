"""
Tests for the analysis module.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.analysis.analysis_engine import AnalysisEngine
from src.indicators.rsi import RSI
from src.indicators.macd import MACD


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


@pytest.fixture
def analysis_engine():
    """Create an AnalysisEngine instance with indicators."""
    engine = AnalysisEngine()
    engine.add_indicator(RSI())
    engine.add_indicator(MACD())
    return engine


def test_analysis_engine_initialization(analysis_engine):
    """Test AnalysisEngine initialization."""
    assert len(analysis_engine.indicators) == 2
    assert isinstance(analysis_engine.indicators[0], RSI)
    assert isinstance(analysis_engine.indicators[1], MACD)


def test_analysis_execution(analysis_engine, sample_data):
    """Test running analysis with multiple indicators."""
    result = analysis_engine.analyze(sample_data)
    
    # Check that all indicator columns are present
    assert 'rsi' in result.columns
    assert 'macd_line' in result.columns
    assert 'signal_line' in result.columns
    assert 'macd_histogram' in result.columns
    
    # Check that signal columns are present
    assert 'rsi_signal' in result.columns
    assert 'macd_signal' in result.columns
    
    # Check composite signal
    assert 'composite_signal' in result.columns
    assert set(result['composite_signal'].unique()).issubset({-1, 0, 1})


def test_add_indicator(analysis_engine):
    """Test adding indicators to the engine."""
    initial_count = len(analysis_engine.indicators)
    
    # Add a new indicator
    analysis_engine.add_indicator(RSI(params={'period': 7}))
    
    assert len(analysis_engine.indicators) == initial_count + 1
    assert isinstance(analysis_engine.indicators[-1], RSI)
    assert analysis_engine.indicators[-1].period == 7


def test_error_handling(analysis_engine):
    """Test error handling in analysis engine."""
    # Test with invalid data
    invalid_data = pd.DataFrame({
        'timestamp': [],
        'close': []
    })
    
    with pytest.raises(ValueError):
        analysis_engine.analyze(invalid_data)