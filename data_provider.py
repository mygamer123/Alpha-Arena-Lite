"""
Data provider abstraction for both live and historical data
"""
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
import pandas as pd
from stockstats import StockDataFrame
from datetime import datetime, timezone
import os
import logging

logger = logging.getLogger(__name__)


class DataProvider(ABC):
    """Abstract base class for data providers"""
    
    @abstractmethod
    def get_last_price(self, symbol: str) -> Optional[float]:
        """Get the last price for a symbol"""
        pass
    
    @abstractmethod
    def get_kline_data(self, symbol: str, period: str = '1d', count: int = 100) -> List[Dict[str, Any]]:
        """Get kline/candlestick data for a symbol"""
        pass


class FileDataProvider(DataProvider):
    """Data provider that reads from local CSV files"""
    
    def __init__(self, data_dir: str = "historical_data"):
        """
        Initialize file-based data provider
        
        Args:
            data_dir: Directory containing historical data CSV files
        """
        self.data_dir = data_dir
        self.data_cache: Dict[str, pd.DataFrame] = {}
        self.current_index: Dict[str, int] = {}
        
    def _load_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Load historical data from CSV file"""
        if symbol in self.data_cache:
            return self.data_cache[symbol]
        
        filename = os.path.join(self.data_dir, f"{symbol}_historical.csv")
        
        if not os.path.exists(filename):
            logger.error(f"Data file not found: {filename}")
            return None
        
        try:
            df = pd.read_csv(filename)
            # Ensure required columns exist
            required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            if not all(col in df.columns for col in required_cols):
                logger.error(f"Missing required columns in {filename}")
                return None
            
            # Convert timestamp to datetime
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
            df = df.sort_values('timestamp')
            
            self.data_cache[symbol] = df
            self.current_index[symbol] = 0
            
            logger.info(f"Loaded {len(df)} rows of data for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading data for {symbol}: {e}")
            return None
    
    def get_last_price(self, symbol: str) -> Optional[float]:
        """Get the last price for a symbol from historical data"""
        df = self._load_data(symbol)
        if df is None or df.empty:
            return None
        
        # Get current index for this symbol
        idx = self.current_index.get(symbol, 0)
        
        if idx >= len(df):
            logger.warning(f"Reached end of data for {symbol}")
            return None
        
        return float(df.iloc[idx]['close'])
    
    def get_kline_data(self, symbol: str, period: str = '1d', count: int = 100) -> List[Dict[str, Any]]:
        """Get kline/candlestick data for a symbol from historical data"""
        df = self._load_data(symbol)
        if df is None or df.empty:
            return []
        
        # Get current index
        idx = self.current_index.get(symbol, 0)
        
        # Get data up to current index
        start_idx = max(0, idx - count + 1)
        end_idx = min(idx + 1, len(df))
        
        if start_idx >= end_idx:
            return []
        
        subset = df.iloc[start_idx:end_idx]
        
        klines = []
        for _, row in subset.iterrows():
            timestamp = int(row['timestamp'])
            open_price = float(row['open'])
            high_price = float(row['high'])
            low_price = float(row['low'])
            close_price = float(row['close'])
            volume = float(row['volume'])
            
            change = close_price - open_price if open_price else 0
            percent = (change / open_price * 100) if open_price else 0
            
            klines.append({
                'timestamp': timestamp,
                'datetime_str': datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat(),
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume,
                'amount': volume * close_price,
                'change': change,
                'percent': percent,
            })
        
        return klines
    
    def advance(self, symbol: str, steps: int = 1) -> bool:
        """
        Advance the current position in historical data
        
        Args:
            symbol: Symbol to advance
            steps: Number of steps to advance
            
        Returns:
            True if advanced successfully, False if reached end of data
        """
        if symbol not in self.data_cache:
            self._load_data(symbol)
        
        if symbol not in self.data_cache:
            return False
        
        df = self.data_cache[symbol]
        current_idx = self.current_index.get(symbol, 0)
        new_idx = current_idx + steps
        
        if new_idx >= len(df):
            logger.debug(f"Reached end of data for {symbol}")
            return False
        
        self.current_index[symbol] = new_idx
        return True
    
    def reset(self, symbol: Optional[str] = None):
        """Reset the current position to the beginning"""
        if symbol:
            self.current_index[symbol] = 0
        else:
            self.current_index = {}
    
    def get_current_timestamp(self, symbol: str) -> Optional[int]:
        """Get the current timestamp for a symbol"""
        df = self._load_data(symbol)
        if df is None or df.empty:
            return None
        
        idx = self.current_index.get(symbol, 0)
        if idx >= len(df):
            return None
        
        return int(df.iloc[idx]['timestamp'])


def symbol_data_provider_json(symbol: str, frequency: str, count: int, 
                                data_provider: DataProvider) -> Dict[str, Any]:
    """
    Get comprehensive market data for a symbol using any data provider
    
    Args:
        symbol: Trading symbol
        frequency: Time frequency (1m, 3m, 5m, 1h, 4h, 1d)
        count: Number of data points
        data_provider: Data provider instance (FileDataProvider or HyperliquidClient)
    
    Returns:
        Dictionary containing market data and technical indicators
    """
    klines = data_provider.get_kline_data(symbol, period=frequency, count=count)
    
    if not klines:
        logger.warning(f"No klines data for {symbol}")
        return {}
    
    df = pd.DataFrame(klines)
    df['datetime'] = pd.to_datetime(df['datetime_str'])
    df = df.set_index('datetime')
    
    stock = StockDataFrame.retype(df[['open', 'high', 'low', 'close', 'volume']])
    
    # Calculate technical indicators
    stock['rsi_7']
    stock['rsi_14']
    stock['macd']
    stock['macds']
    stock['close_20_ema']
    stock['atr_3']
    stock['atr_14']
    stock['close_50_ema']
    
    latest = stock.tail(1)
    historical_data = stock.tail(count)
    
    mid_prices = ((historical_data['high'] + historical_data['low']) / 2).tolist()
    
    result = {
        'current_price': float(latest['close'].iloc[0]),
        'current_close_20_ema': float(latest['close_20_ema'].iloc[0]),
        'current_macd': float(latest['macd'].iloc[0]),
        'current_rsi_7': float(latest['rsi_7'].iloc[0]),
        'current_volume': float(latest['volume'].iloc[0]),
        'average_volume': float(historical_data['volume'].mean()),
        'open_interest_latest': float(latest['volume'].iloc[0]),
        'open_interest_average': float(historical_data['volume'].mean()),
        'funding_rate': 0.0,
        'mid_prices': mid_prices,
        'ema_close_20_array': historical_data['close_20_ema'].tolist(),
        'macd_array': historical_data['macd'].tolist(),
        'rsi_7_array': historical_data['rsi_7'].tolist(),
        'rsi_14_array': historical_data['rsi_14'].tolist(),
        'ema_20_array': historical_data['close_20_ema'].tolist(),
        'ema_50_array': historical_data['close_50_ema'].tolist(),
        'atr_3_array': historical_data['atr_3'].tolist(),
        'atr_14_array': historical_data['atr_14'].tolist()
    }
    
    return result
