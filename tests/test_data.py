"""
Tests for the data module.
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from src.data.data_fetcher import DataFetcher
from src.data.data_preprocessing import DataPreprocessor


def test_data_fetcher_initialization():
    """Test DataFetcher initialization."""
    fetcher = DataFetcher(api_key="test_key")
    assert fetcher.api_key == "test_key"


def test_load_from_csv():
    """Test loading data from CSV."""
    # Create test CSV file
    test_data = pd.DataFrame({
        'timestamp': [datetime.now() - timedelta(minutes=i) for i in range(10)],
        'open': [100 + i for i in range(10)],
        'high': [105 + i for i in range(10)],
        'low': [95 + i for i in range(10)],
        'close': [102 + i for i in range(10)],
        'volume': [1000 + i for i in range(10)]
    })
    
    test_file = 'test_data.csv'
    test_data.to_csv(test_file, index=False)
    
    # Test loading
    fetcher = DataFetcher()
    loaded_data = fetcher.load_from_csv(test_file)
    
    assert isinstance(loaded_data, pd.DataFrame)
    assert all(col in loaded_data.columns for col in ['open', 'high', 'low', 'close', 'volume'])
    assert len(loaded_data) == 10


def test_data_preprocessing():
    """Test data preprocessing functions."""
    preprocessor = DataPreprocessor()
    
    # Create test data
    test_data = pd.DataFrame({
        'timestamp': [datetime.now() - timedelta(minutes=i) for i in range(5)],
        'open': [100, 101, None, 103, 104],
        'high': [105, 106, 107, 108, 109],
        'low': [95, 96, 97, 98, 99],
        'close': [102, 103, 104, 105, 106],
        'volume': [1000, 1100, 1200, 1300, 1400]
    })
    
    # Test cleaning
    cleaned_data = preprocessor.clean_data(test_data)
    assert len(cleaned_data) == 4  # One row had None
    assert cleaned_data['open'].isna().sum() == 0
    
    # Test feature engineering
    engineered_data = preprocessor.engineer_features(cleaned_data)
    assert 'returns' in engineered_data.columns
    assert 'log_returns' in engineered_data.columns
    assert 'volume_base' in engineered_data.columns
    
    # Test normalization
    normalized_data = preprocessor.normalize_features(
        cleaned_data,
        columns=['close'],
        method='minmax'
    )
    assert 'close_norm' in normalized_data.columns
    assert normalized_data['close_norm'].max() <= 1
    assert normalized_data['close_norm'].min() >= 0