"""
Test OpenRouter configuration loading
"""
import os
import pytest
from unittest.mock import patch


def test_openrouter_config_loading():
    """Test that OpenRouter configuration is loaded correctly from environment"""
    with patch.dict(os.environ, {
        'OPENROUTER_API_KEY': 'test-key',
        'OPENROUTER_MODEL': 'test-model'
    }):
        # Re-import to pick up new env vars
        import importlib
        import trade_decision_simple_AI
        importlib.reload(trade_decision_simple_AI)
        
        assert trade_decision_simple_AI.OPENROUTER_API_KEY == 'test-key'
        assert trade_decision_simple_AI.OPENROUTER_MODEL == 'test-model'


def test_openrouter_model_default():
    """Test that OpenRouter model has a sensible default"""
    with patch.dict(os.environ, {
        'OPENROUTER_API_KEY': 'test-key'
    }, clear=True):
        # Re-import to pick up new env vars
        import importlib
        import trade_decision_simple_AI
        importlib.reload(trade_decision_simple_AI)
        
        assert trade_decision_simple_AI.OPENROUTER_MODEL == 'anthropic/claude-3.5-sonnet'


def test_openai_key_loading():
    """Test that OpenAI key is still loaded correctly"""
    with patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test-openai-key'
    }, clear=True):
        # Re-import to pick up new env vars
        import importlib
        import trade_decision_simple_AI
        importlib.reload(trade_decision_simple_AI)
        
        assert trade_decision_simple_AI.OPENAI_API_KEY == 'test-openai-key'
