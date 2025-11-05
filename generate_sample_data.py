"""
Generate sample historical data for backtesting
This script creates realistic-looking historical price data for testing
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_historical_data(symbol: str, days: int = 30, interval_minutes: int = 3, 
                             start_price: float = 50000.0, volatility: float = 0.02,
                             random_seed: int = 42):
    """
    Generate synthetic historical data for a cryptocurrency
    
    Args:
        symbol: Trading symbol (e.g., 'BTC', 'ETH')
        days: Number of days of historical data
        interval_minutes: Time interval in minutes (e.g., 3 for 3-minute candles)
        start_price: Starting price
        volatility: Price volatility (standard deviation of returns)
        random_seed: Random seed for reproducibility (default: 42)
    
    Returns:
        DataFrame with historical data
    """
    # Calculate number of candles
    candles_per_day = 24 * 60 // interval_minutes
    total_candles = days * candles_per_day
    
    # Generate timestamps
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    timestamps = [start_time + timedelta(minutes=i*interval_minutes) for i in range(total_candles)]
    
    # Generate price data using random walk
    np.random.seed(random_seed)  # For reproducibility
    returns = np.random.normal(0, volatility, total_candles)
    
    # Add some trend
    trend = np.linspace(0, 0.1, total_candles)  # 10% upward trend over the period
    returns += trend / total_candles
    
    # Calculate prices using cumulative returns
    prices = start_price * np.exp(np.cumsum(returns))
    
    # Generate OHLC data
    data = []
    for i, (ts, close) in enumerate(zip(timestamps, prices)):
        # Generate realistic OHLC from close price
        volatility_factor = np.random.uniform(0.005, 0.015)
        high = close * (1 + volatility_factor)
        low = close * (1 - volatility_factor)
        
        # Ensure open is between high and low
        if i == 0:
            open_price = start_price
        else:
            open_price = prices[i-1]
        
        # Adjust high/low if needed
        high = max(high, open_price, close)
        low = min(low, open_price, close)
        
        # Generate volume
        volume = np.random.uniform(50, 200)
        
        data.append({
            'timestamp': int(ts.timestamp()),
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close, 2),
            'volume': round(volume, 2)
        })
    
    df = pd.DataFrame(data)
    return df


def main():
    """Generate sample data for multiple symbols"""
    # Create historical_data directory if it doesn't exist
    os.makedirs('historical_data', exist_ok=True)
    
    # Generate data for different symbols
    symbols_config = [
        {'symbol': 'BTC', 'start_price': 45000.0, 'volatility': 0.02},
        {'symbol': 'ETH', 'start_price': 3000.0, 'volatility': 0.025},
        {'symbol': 'SOL', 'start_price': 100.0, 'volatility': 0.03},
    ]
    
    for config in symbols_config:
        symbol = config['symbol']
        print(f"Generating historical data for {symbol}...")
        
        df = generate_historical_data(
            symbol=symbol,
            days=30,
            interval_minutes=3,
            start_price=config['start_price'],
            volatility=config['volatility']
        )
        
        # Save to CSV
        filename = f"historical_data/{symbol}_historical.csv"
        df.to_csv(filename, index=False)
        
        print(f"  ✅ Saved {len(df)} candles to {filename}")
        print(f"  Price range: ${df['low'].min():.2f} - ${df['high'].max():.2f}")
        print(f"  Date range: {datetime.fromtimestamp(df['timestamp'].min()).strftime('%Y-%m-%d %H:%M')} to {datetime.fromtimestamp(df['timestamp'].max()).strftime('%Y-%m-%d %H:%M')}")
        print()

if __name__ == "__main__":
    main()
