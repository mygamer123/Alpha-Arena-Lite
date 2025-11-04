"""
Simple Backtest Simulation - Test data provider without AI decisions
This is useful for validating the backtest infrastructure without needing API keys
"""
import time
from datetime import datetime
from typing import Dict, Any, Optional
from data_provider import FileDataProvider, symbol_data_provider_json
from simple_portfolio import SimplePortfolio

# Configuration constants
SYMBOLS = ['BTC', 'ETH', 'SOL']
UPDATE_FREQUENCY = '3m'
KLINE_COUNT = 10
DATA_DIR = 'historical_data'
MAX_ITERATIONS = 20  # Limit iterations for quick testing


def safe_fetch_market_data(symbol: str, data_provider: FileDataProvider) -> Optional[Dict[str, Any]]:
    """Safely fetch market data for a symbol with error handling"""
    try:
        json_result = symbol_data_provider_json(symbol, UPDATE_FREQUENCY, KLINE_COUNT, data_provider)
        if not json_result or 'current_price' not in json_result:
            print(f"⚠️  {symbol}: No valid kline data returned")
            return None
        return json_result
    except Exception as e:
        print(f"❌ {symbol}: Error fetching market data: {e}")
        return None


def main():
    # Initialize file-based data provider
    print("📁 Initializing file-based data provider...")
    data_provider = FileDataProvider(data_dir=DATA_DIR)
    
    # Create portfolio
    portfolio = SimplePortfolio()
    print(f"Initial Cash: ${portfolio.initial_cash:,.2f}")
    
    # Check if we have data for all symbols
    print("\n🔍 Checking data availability...")
    all_symbols_available = True
    for symbol in SYMBOLS:
        timestamp = data_provider.get_current_timestamp(symbol)
        if timestamp:
            dt = datetime.fromtimestamp(timestamp)
            print(f"✅ {symbol}: Data available (starting from {dt.strftime('%Y-%m-%d %H:%M:%S')})")
        else:
            print(f"❌ {symbol}: No data available")
            all_symbols_available = False
    
    if not all_symbols_available:
        print("\n⚠️  Some symbols don't have data. Please run 'python generate_sample_data.py' to create sample data.")
        return
    
    print("\n" + "="*80)
    print("🚀 Starting simple backtest (no AI decisions)")
    print("="*80)
    
    loop_count = 0
    
    while loop_count < MAX_ITERATIONS:
        loop_count += 1
        
        # Get current timestamp for display
        first_symbol = SYMBOLS[0]
        current_ts = data_provider.get_current_timestamp(first_symbol)
        current_time = datetime.fromtimestamp(current_ts) if current_ts else datetime.now()
        
        print(f"\n📅 {current_time.strftime('%Y-%m-%d %H:%M:%S')} - Iteration #{loop_count}")
        
        # Fetch market data for each symbol
        for symbol in SYMBOLS:
            json_result = safe_fetch_market_data(symbol, data_provider)
            if json_result is None:
                continue
            
            current_price = json_result['current_price']
            rsi = json_result.get('current_rsi_7', 0)
            macd = json_result.get('current_macd', 0)
            
            print(f"  {symbol}: ${current_price:,.2f} (RSI: {rsi:.2f}, MACD: {macd:.2f})")
            
            # Update portfolio prices
            portfolio.update_price(symbol, current_price)
        
        # Advance all symbols to next time step
        all_advanced = True
        for symbol in SYMBOLS:
            if not data_provider.advance(symbol, steps=1):
                all_advanced = False
                break
        
        if not all_advanced:
            print(f"\n✅ Reached end of historical data after {loop_count} iterations")
            break
    
    print("\n" + "="*80)
    print("✅ Backtest complete!")
    print(f"📊 Total iterations: {loop_count}")
    print("="*80)
    
    # Display final results
    portfolio.display()


if __name__ == "__main__":
    main()
