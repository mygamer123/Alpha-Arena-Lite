"""
Test OpenRouter integration in trade decision provider
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json


@patch('trade_decision_simple_AI.OPENROUTER_API_KEY', 'test-openrouter-key')
@patch('trade_decision_simple_AI.OPENROUTER_MODEL', 'test-model')
@patch('trade_decision_simple_AI.OPENAI_API_KEY', None)
def test_trade_decision_uses_openrouter():
    """Test that trade_decision_provider uses OpenRouter when configured"""
    from trade_decision_simple_AI import trade_decision_provider
    
    # Mock market data
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
    
    # Mock portfolio
    portfolio_json = {
        'timestamp': '2024-01-01T00:00:00',
        'initial_cash': 10000.0,
        'total_asset': 10000.0,
        'available_cash': 10000.0,
        'total_pnl': 0.0,
        'positions': []
    }
    
    # Mock OpenAI client and response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = json.dumps({
        'trade_signal_args': {
            'coin': 'BTC',
            'signal': 'buy',
            'quantity': 0.1,
            'profit_target': 55000.0,
            'stop_loss': 48000.0,
            'invalidation_condition': 'If the price closes below 48000.00 on a 3-minute candle',
            'leverage': 5,
            'confidence': 0.75,
            'risk_usd': 100.0,
            'entry_price': 50000.0
        }
    })
    
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    
    with patch('openai.OpenAI', return_value=mock_client) as mock_openai:
        # Call the function
        result = trade_decision_provider(market_data, portfolio_json)
        
        # Verify OpenAI was called with OpenRouter configuration
        mock_openai.assert_called_once()
        call_kwargs = mock_openai.call_args.kwargs
        assert call_kwargs['api_key'] == 'test-openrouter-key'
        assert call_kwargs['base_url'] == 'https://openrouter.ai/api/v1'
        
        # Verify the API call used the correct model
        mock_client.chat.completions.create.assert_called_once()
        create_call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert create_call_kwargs['model'] == 'test-model'
        
        # Verify result format
        assert 'BTC' in result
        assert 'trade_signal_args' in result['BTC']


@patch('trade_decision_simple_AI.OPENROUTER_API_KEY', None)
@patch('trade_decision_simple_AI.OPENAI_API_KEY', 'test-openai-key')
def test_trade_decision_uses_deepseek_when_no_openrouter():
    """Test that trade_decision_provider uses DeepSeek when OpenRouter is not configured"""
    from trade_decision_simple_AI import trade_decision_provider
    
    # Mock market data
    market_data = {
        'ETH': {
            'current_price': 3000.0,
            'frequency': '3m',
            'current_close_20_ema': 2950.0,
            'current_macd': 50.0,
            'current_rsi_7': 55.0,
            'open_interest_latest': 500000.0,
            'open_interest_average': 480000.0,
            'funding_rate': 0.0002,
            'mid_prices': [2900, 2950, 3000],
            'ema_20_array': [2900, 2925, 2950],
            'macd_array': [30, 40, 50],
            'rsi_7_array': [50, 52, 55],
            'rsi_14_array': [48, 50, 53]
        }
    }
    
    # Mock portfolio
    portfolio_json = {
        'timestamp': '2024-01-01T00:00:00',
        'initial_cash': 10000.0,
        'total_asset': 10000.0,
        'available_cash': 10000.0,
        'total_pnl': 0.0,
        'positions': []
    }
    
    # Mock OpenAI client and response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = json.dumps({
        'trade_signal_args': {
            'coin': 'ETH',
            'signal': 'hold',
            'quantity': 0.0,
            'profit_target': 3200.0,
            'stop_loss': 2800.0,
            'invalidation_condition': 'If the price closes below 2800.00 on a 3-minute candle',
            'leverage': 3,
            'confidence': 0.5,
            'risk_usd': 0.0,
            'entry_price': 3000.0
        }
    })
    
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    
    with patch('openai.OpenAI', return_value=mock_client) as mock_openai:
        # Call the function
        result = trade_decision_provider(market_data, portfolio_json)
        
        # Verify OpenAI was called with DeepSeek configuration
        mock_openai.assert_called_once()
        call_kwargs = mock_openai.call_args.kwargs
        assert call_kwargs['api_key'] == 'test-openai-key'
        assert call_kwargs['base_url'] == 'https://api.deepseek.com/v1'
        
        # Verify the API call used the correct model
        mock_client.chat.completions.create.assert_called_once()
        create_call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert create_call_kwargs['model'] == 'deepseek-chat'
        
        # Verify result format
        assert 'ETH' in result
        assert 'trade_signal_args' in result['ETH']
