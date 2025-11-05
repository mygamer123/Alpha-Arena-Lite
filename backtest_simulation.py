"""
Backtest Simulation - Test strategies using historical data from local files
"""
import time
import signal
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from data_provider import FileDataProvider, symbol_data_provider_json
from simple_portfolio import SimplePortfolio
from trade_decision_simple_AI import trade_decision_provider

# Configuration constants
SYMBOLS = ['BTC', 'ETH', 'SOL']
PORTFOLIO_FILE = 'backtest_portfolio.json'
PORTFOLIO_INIT_FILE = 'portfolio_init.json'
UPDATE_FREQUENCY = '3m'
KLINE_COUNT = 10
DISPLAY_INTERVAL = 100  # Display portfolio every N loops
DATA_DIR = 'historical_data'

# Load environment variables
load_dotenv()

# Global shutdown flag for graceful shutdown
shutdown = False


def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    global shutdown
    print("\n\n⚠️  Shutdown signal received. Finishing current loop...")
    shutdown = True


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


# Set up signal handlers for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Initialize file-based data provider
print("📁 Initializing file-based data provider...")
data_provider = FileDataProvider(data_dir=DATA_DIR)

# Load or create portfolio
portfolio = SimplePortfolio()

try:
    portfolio.load_from_file(PORTFOLIO_INIT_FILE)
    print("✅ Loaded existing portfolio configuration")
    print(f"Initial Cash: ${portfolio.initial_cash:,.2f}")
    print(f"Available Cash: ${portfolio.available_cash:,.2f}")
    portfolio.display()
except FileNotFoundError:
    print("📝 Creating new portfolio")
    print(f"Initial Cash: ${portfolio.initial_cash:,.2f}")
except Exception as e:
    print(f"❌ Error loading portfolio: {e}")
    print("📝 Starting with new portfolio")

loop_count = 0
portfolio_changed = False

print("\n🚀 Starting backtest simulation. Press Ctrl+C to stop gracefully.\n")
print(f"📊 Data source: Local CSV files in '{DATA_DIR}/' directory\n")

# Check if we have data for all symbols
print("🔍 Checking data availability...")
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
    exit(1)

print("\n" + "="*80)

while not shutdown:
    try:
        loop_count += 1
        
        # Get current timestamp for display
        first_symbol = SYMBOLS[0]
        current_ts = data_provider.get_current_timestamp(first_symbol)
        current_time = datetime.fromtimestamp(current_ts) if current_ts else datetime.now()
        
        if loop_count % DISPLAY_INTERVAL == 0 or loop_count == 1:
            print(f"\n{current_time.strftime('%Y-%m-%d %H:%M:%S')} - Loop #{loop_count} - Fetching market data...")
        
        market_data_for_decisions_json = {}
        successful_fetches = 0
        
        # Fetch market data for each symbol
        for symbol in SYMBOLS:
            json_result = safe_fetch_market_data(symbol, data_provider)
            if json_result is None:
                continue
            
            # Add symbol and frequency to json_result
            json_result['symbol'] = symbol
            json_result['frequency'] = UPDATE_FREQUENCY
            
            current_price = json_result['current_price']
            
            if loop_count % DISPLAY_INTERVAL == 0 or loop_count == 1:
                print(f"✅ {symbol}: ${current_price:,.2f}")
            
            # Update portfolio prices
            portfolio.update_price(symbol, current_price)
            portfolio.update_unrealized_pnl(symbol)
            market_data_for_decisions_json[symbol] = json_result
            successful_fetches += 1
        
        # Skip decision making if no market data was fetched
        if successful_fetches == 0:
            print("⚠️  No market data fetched for any symbol. Ending backtest.")
            break
        
        # Display portfolio (at intervals or when changed)
        if loop_count % DISPLAY_INTERVAL == 0 or portfolio_changed or loop_count == 1:
            portfolio.display()
        
        portfolio_json = portfolio.return_json()
        
        # Generate trading decisions
        if loop_count % DISPLAY_INTERVAL == 0 or loop_count == 1:
            print("\n📊 Generating Trading Decisions...")
        
        try:
            all_decisions = trade_decision_provider(market_data_for_decisions_json, portfolio_json)
        except Exception as e:
            print(f"❌ Error generating trading decisions: {e}")
            all_decisions = {}
        
        if not all_decisions:
            if loop_count % DISPLAY_INTERVAL == 0 or loop_count == 1:
                print("\n⏸️  No new trading signals generated.")
        else:
            portfolio.decisions_display(all_decisions)
            
            print("\n📝 Executing Orders...")
            portfolio_changed = False
            
            for symbol, decision_data in all_decisions.items():
                if portfolio.execute_decision(symbol=symbol, decision_data=decision_data):
                    portfolio_changed = True
        
        if loop_count % DISPLAY_INTERVAL == 0 or loop_count == 1:
            print("\n" + "="*80)
        
        # Save portfolio only if it changed
        if portfolio_changed:
            try:
                portfolio.save_to_file(PORTFOLIO_FILE)
                if loop_count % DISPLAY_INTERVAL == 0 or loop_count == 1:
                    print("💾 Portfolio saved to file")
            except Exception as e:
                print(f"❌ Error saving portfolio: {e}")
        
        # Display portfolio metrics
        if loop_count % DISPLAY_INTERVAL == 0 or loop_count == 1:
            total_pnl = portfolio.total_pnl()
            total_return = ((portfolio.total_asset - portfolio.initial_cash) / portfolio.initial_cash * 100) if portfolio.initial_cash > 0 else 0
            print(f"\n💰 Portfolio Metrics:")
            print(f"  Available Cash: ${portfolio.available_cash:,.2f}")
            print(f"  Total Asset Value: ${portfolio.total_asset:,.2f}")
            print(f"  Total Unrealized PnL: ${total_pnl:,.2f}")
            print(f"  Total Return: {total_return:.2f}%")
        
        # Advance all symbols to next time step
        all_advanced = True
        for symbol in SYMBOLS:
            if not data_provider.advance(symbol, steps=1):
                all_advanced = False
                break
        
        if not all_advanced:
            print(f"\n✅ Reached end of historical data after {loop_count} iterations")
            break
        
    except KeyboardInterrupt:
        # This should be caught by signal handler, but just in case
        break
    except Exception as e:
        print(f"\n❌ Unexpected error in main loop: {e}")
        print("Continuing to next iteration...")

# Final save on shutdown
print("\n\n🛑 Backtest complete!")
print(f"📊 Total iterations: {loop_count}")

try:
    portfolio.save_to_file(PORTFOLIO_FILE)
    print(f"✅ Portfolio saved to {PORTFOLIO_FILE}")
except Exception as e:
    print(f"❌ Error saving portfolio on shutdown: {e}")

# Display final results
print("\n" + "="*80)
print("📈 Final Backtest Results")
print("="*80)
portfolio.display()

total_pnl = portfolio.total_pnl()
total_return = ((portfolio.total_asset - portfolio.initial_cash) / portfolio.initial_cash * 100) if portfolio.initial_cash > 0 else 0

print(f"\n💰 Final Metrics:")
print(f"  Initial Cash: ${portfolio.initial_cash:,.2f}")
print(f"  Final Asset Value: ${portfolio.total_asset:,.2f}")
print(f"  Total Return: {total_return:.2f}%")
print(f"  Total PnL: ${total_pnl:,.2f}")

print("\n👋 Backtest finished.")
