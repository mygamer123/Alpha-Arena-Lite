"""
Tests for data provider functionality
"""
import pytest
import os
import tempfile
import pandas as pd
from data_provider import FileDataProvider, symbol_data_provider_json


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_data():
    """Generate sample historical data"""
    data = []
    base_timestamp = 1699999800
    base_price = 45000.0
    
    for i in range(100):
        timestamp = base_timestamp + (i * 180)  # 3-minute intervals
        price = base_price + (i * 10)  # Simple upward trend
        
        data.append({
            'timestamp': timestamp,
            'open': price,
            'high': price + 50,
            'low': price - 50,
            'close': price + 25,
            'volume': 100.0 + i
        })
    
    return pd.DataFrame(data)


def test_file_data_provider_initialization(temp_data_dir):
    """Test FileDataProvider initialization"""
    provider = FileDataProvider(data_dir=temp_data_dir)
    assert provider.data_dir == temp_data_dir
    assert provider.data_cache == {}
    assert provider.current_index == {}


def test_file_data_provider_load_missing_file(temp_data_dir):
    """Test loading data when file doesn't exist"""
    provider = FileDataProvider(data_dir=temp_data_dir)
    price = provider.get_last_price('BTC')
    assert price is None


def test_file_data_provider_load_data(temp_data_dir, sample_data):
    """Test loading data from CSV file"""
    # Create sample CSV file
    csv_path = os.path.join(temp_data_dir, 'BTC_historical.csv')
    sample_data.to_csv(csv_path, index=False)
    
    provider = FileDataProvider(data_dir=temp_data_dir)
    price = provider.get_last_price('BTC')
    
    assert price is not None
    assert price == sample_data.iloc[0]['close']


def test_file_data_provider_advance(temp_data_dir, sample_data):
    """Test advancing through historical data"""
    csv_path = os.path.join(temp_data_dir, 'BTC_historical.csv')
    sample_data.to_csv(csv_path, index=False)
    
    provider = FileDataProvider(data_dir=temp_data_dir)
    
    # Get initial price
    price1 = provider.get_last_price('BTC')
    
    # Advance one step
    advanced = provider.advance('BTC', steps=1)
    assert advanced is True
    
    # Get new price
    price2 = provider.get_last_price('BTC')
    
    # Prices should be different
    assert price1 != price2
    assert price2 == sample_data.iloc[1]['close']


def test_file_data_provider_advance_beyond_end(temp_data_dir, sample_data):
    """Test advancing beyond the end of data"""
    csv_path = os.path.join(temp_data_dir, 'BTC_historical.csv')
    sample_data.to_csv(csv_path, index=False)
    
    provider = FileDataProvider(data_dir=temp_data_dir)
    
    # Advance to the end
    for _ in range(len(sample_data) - 1):
        provider.advance('BTC', steps=1)
    
    # Try to advance beyond end
    advanced = provider.advance('BTC', steps=1)
    assert advanced is False


def test_file_data_provider_reset(temp_data_dir, sample_data):
    """Test resetting data position"""
    csv_path = os.path.join(temp_data_dir, 'BTC_historical.csv')
    sample_data.to_csv(csv_path, index=False)
    
    provider = FileDataProvider(data_dir=temp_data_dir)
    
    # Get initial price
    price1 = provider.get_last_price('BTC')
    
    # Advance several steps
    provider.advance('BTC', steps=5)
    price2 = provider.get_last_price('BTC')
    assert price1 != price2
    
    # Reset
    provider.reset('BTC')
    price3 = provider.get_last_price('BTC')
    
    # Should be back to initial price
    assert price1 == price3


def test_file_data_provider_get_kline_data(temp_data_dir, sample_data):
    """Test getting kline data"""
    csv_path = os.path.join(temp_data_dir, 'BTC_historical.csv')
    sample_data.to_csv(csv_path, index=False)
    
    provider = FileDataProvider(data_dir=temp_data_dir)
    
    # Advance to position where we have enough history
    provider.advance('BTC', steps=20)
    
    # Get kline data
    klines = provider.get_kline_data('BTC', period='3m', count=10)
    
    assert len(klines) == 10
    assert 'timestamp' in klines[0]
    assert 'open' in klines[0]
    assert 'high' in klines[0]
    assert 'low' in klines[0]
    assert 'close' in klines[0]
    assert 'volume' in klines[0]


def test_symbol_data_provider_json_with_file_provider(temp_data_dir, sample_data):
    """Test symbol_data_provider_json with FileDataProvider"""
    csv_path = os.path.join(temp_data_dir, 'BTC_historical.csv')
    sample_data.to_csv(csv_path, index=False)
    
    provider = FileDataProvider(data_dir=temp_data_dir)
    
    # Advance to ensure enough history for indicators
    provider.advance('BTC', steps=50)
    
    # Get market data with indicators
    result = symbol_data_provider_json('BTC', '3m', 10, provider)
    
    assert result is not None
    assert 'current_price' in result
    assert 'current_rsi_7' in result
    assert 'current_macd' in result
    assert 'mid_prices' in result
    assert isinstance(result['mid_prices'], list)


def test_file_data_provider_get_current_timestamp(temp_data_dir, sample_data):
    """Test getting current timestamp"""
    csv_path = os.path.join(temp_data_dir, 'BTC_historical.csv')
    sample_data.to_csv(csv_path, index=False)
    
    provider = FileDataProvider(data_dir=temp_data_dir)
    
    timestamp = provider.get_current_timestamp('BTC')
    assert timestamp == sample_data.iloc[0]['timestamp']
    
    # Advance and check again
    provider.advance('BTC', steps=5)
    timestamp2 = provider.get_current_timestamp('BTC')
    assert timestamp2 == sample_data.iloc[5]['timestamp']


def test_file_data_provider_path_traversal_protection(temp_data_dir):
    """Test that path traversal attempts are blocked"""
    provider = FileDataProvider(data_dir=temp_data_dir)
    
    # Test various path traversal attempts
    malicious_symbols = [
        '../etc/passwd',
        '../../etc/passwd',
        'BTC/../../../etc/passwd',
        'BTC/../../secret',
        '..\\..\\windows\\system32',
    ]
    
    for symbol in malicious_symbols:
        price = provider.get_last_price(symbol)
        assert price is None, f"Path traversal not blocked for: {symbol}"


def test_file_data_provider_invalid_symbol_format(temp_data_dir):
    """Test that invalid symbol formats are rejected"""
    provider = FileDataProvider(data_dir=temp_data_dir)
    
    # Test invalid characters
    invalid_symbols = [
        'BTC/USD',
        'BTC:USDT',
        'BTC;rm -rf',
        'BTC|cat',
        'BTC`whoami`',
        'BTC$(ls)',
    ]
    
    for symbol in invalid_symbols:
        price = provider.get_last_price(symbol)
        assert price is None, f"Invalid symbol format not rejected: {symbol}"
