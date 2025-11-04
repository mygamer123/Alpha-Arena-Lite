"""
Test API key validation in trade decision provider
"""
import pytest
from unittest.mock import patch


@patch('trade_decision_simple_AI.OPENROUTER_API_KEY', None)
@patch('trade_decision_simple_AI.OPENAI_API_KEY', None)
def test_trade_decision_raises_when_no_api_key():
    """Test that trade_decision_provider raises an error when no API key is configured"""
    from trade_decision_simple_AI import trade_decision_provider
    
    market_data = {
        'BTC': {
            'current_price': 50000.0,
            'frequency': '3m',
            'current_close_20_ema': 49500.0,
            'current_macd': 100.0,
            'current_rsi_7': 65.0,
            'open_interest_latest': 1000000.0,
            'open_interest_average': 950000.0,
            'funding_rate': 0.0001,
            'mid_prices': [49000, 49500, 50000],
            'ema_20_array': [49000, 49250, 49500],
            'macd_array': [50, 75, 100],
            'rsi_7_array': [60, 62, 65],
            'rsi_14_array': [58, 60, 63]
        }
    }
    
    portfolio_json = {
        'timestamp': '2024-01-01T00:00:00',
        'initial_cash': 10000.0,
        'total_asset': 10000.0,
        'available_cash': 10000.0,
        'total_pnl': 0.0,
        'positions': []
    }
    
    with pytest.raises(ValueError, match="No valid API key found"):
        trade_decision_provider(market_data, portfolio_json)


@patch('trade_decision_simple_AI.OPENROUTER_API_KEY', '')
@patch('trade_decision_simple_AI.OPENAI_API_KEY', None)
def test_trade_decision_raises_when_openrouter_key_empty():
    """Test that trade_decision_provider raises an error when OpenRouter API key is empty (falls back to checking OpenAI key)"""
    from trade_decision_simple_AI import trade_decision_provider
    
    market_data = {
        'BTC': {
            'current_price': 50000.0,
            'frequency': '3m',
            'current_close_20_ema': 49500.0,
            'current_macd': 100.0,
            'current_rsi_7': 65.0,
            'open_interest_latest': 1000000.0,
            'open_interest_average': 950000.0,
            'funding_rate': 0.0001,
            'mid_prices': [49000, 49500, 50000],
            'ema_20_array': [49000, 49250, 49500],
            'macd_array': [50, 75, 100],
            'rsi_7_array': [60, 62, 65],
            'rsi_14_array': [58, 60, 63]
        }
    }
    
    portfolio_json = {
        'timestamp': '2024-01-01T00:00:00',
        'initial_cash': 10000.0,
        'total_asset': 10000.0,
        'available_cash': 10000.0,
        'total_pnl': 0.0,
        'positions': []
    }
    
    # Empty string is falsy, so it will fall back to checking if any valid key exists
    with pytest.raises(ValueError, match="No valid API key found"):
        trade_decision_provider(market_data, portfolio_json)


@patch('trade_decision_simple_AI.OPENROUTER_API_KEY', None)
@patch('trade_decision_simple_AI.OPENAI_API_KEY', '   ')
def test_trade_decision_raises_when_openai_key_whitespace():
    """Test that trade_decision_provider raises an error when OpenAI API key is only whitespace"""
    from trade_decision_simple_AI import trade_decision_provider
    
    market_data = {
        'BTC': {
            'current_price': 50000.0,
            'frequency': '3m',
            'current_close_20_ema': 49500.0,
            'current_macd': 100.0,
            'current_rsi_7': 65.0,
            'open_interest_latest': 1000000.0,
            'open_interest_average': 950000.0,
            'funding_rate': 0.0001,
            'mid_prices': [49000, 49500, 50000],
            'ema_20_array': [49000, 49250, 49500],
            'macd_array': [50, 75, 100],
            'rsi_7_array': [60, 62, 65],
            'rsi_14_array': [58, 60, 63]
        }
    }
    
    portfolio_json = {
        'timestamp': '2024-01-01T00:00:00',
        'initial_cash': 10000.0,
        'total_asset': 10000.0,
        'available_cash': 10000.0,
        'total_pnl': 0.0,
        'positions': []
    }
    
    with pytest.raises(ValueError, match="No valid API key found"):
        trade_decision_provider(market_data, portfolio_json)
