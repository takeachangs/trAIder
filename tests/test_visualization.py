"""
Tests for the visualization module.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.visualization.charting import ChartBuilder, SignalVisualizer
from src.visualization.dashboard import Dashboard


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
        'volume': np.random.randint(1000, 2000, 100),
        'rsi': np.random.uniform(20, 80, 100),
        'macd_line': np.random.normal(0, 1, 100),
        'signal_line': np.random.normal(0, 1, 100),
        'macd_histogram': np.random.normal(0, 0.5, 100)
    })
    
    return df.sort_values('timestamp')


@pytest.fixture
def chart_builder():
    """Create a ChartBuilder instance."""
    return ChartBuilder(theme='dark')


@pytest.fixture
def dashboard():
    """Create a Dashboard instance."""
    return Dashboard(theme='dark')


def test_chart_builder_initialization(chart_builder):
    """Test ChartBuilder initialization."""
    assert chart_builder.theme == 'dark'
    assert isinstance(chart_builder.layout_defaults, dict)


def test_candlestick_chart_creation(chart_builder, sample_data):
    """Test creating candlestick chart."""
    fig = chart_builder.create_candlestick_chart(sample_data, show_volume=True)
    
    # Check figure properties
    assert fig is not None
    assert len(fig.data) >= 2  # Should have at least candlesticks and volume


def test_indicator_chart_creation(chart_builder, sample_data):
    """Test creating indicator charts."""
    fig = chart_builder.create_indicator_chart(
        sample_data,
        'rsi',
        upper_bound=70,
        lower_bound=30
    )
    
    assert fig is not None
    assert len(fig.data) >= 1


def test_dashboard_creation(dashboard, sample_data):
    """Test creating complete dashboard."""
    indicators = {
        'rsi': sample_data['rsi'],
        'macd_line': sample_data['macd_line'],
        'signal_line': sample_data['signal_line']
    }
    
    signals = {
        'trading_signal': pd.Series(np.random.choice([-1, 0, 1], len(sample_data)))
    }
    
    charts = dashboard.create_trading_dashboard(
        sample_data,
        indicators,
        signals
    )
    
    assert isinstance(charts, dict)
    assert 'main_chart' in charts
    assert any(key.endswith('_chart') for key in charts.keys())


def test_signal_visualization(chart_builder, sample_data):
    """Test adding trading signals to charts."""
    # Create sample signals
    sample_data['signal'] = np.random.choice([-1, 0, 1], len(sample_data))
    
    # Create base chart
    fig = chart_builder.create_candlestick_chart(sample_data)
    
    # Add signals
    visualizer = SignalVisualizer()
    fig_with_signals = visualizer.add_signals_to_chart(
        fig,
        sample_data,
        'signal'
    )
    
    assert fig_with_signals is not None
    assert len(fig_with_signals.data) > len(fig.data)