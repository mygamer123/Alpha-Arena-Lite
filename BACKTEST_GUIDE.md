# 回测功能详细说明 / Backtest Feature Guide

## 概述 / Overview

回测功能允许您使用历史数据测试交易策略，而无需连接到实时交易所。这对于策略开发、验证和优化非常有用。

The backtest feature allows you to test trading strategies using historical data without connecting to live exchanges. This is useful for strategy development, validation, and optimization.

## 数据源说明 / Data Source

### 实时交易模式 (simulation.py)
- **数据源**: Hyperliquid 交易所
- **访问方式**: CCXT 库
- **数据类型**: 实时价格、K线数据、技术指标

### 回测模式 (backtest_simulation.py)
- **数据源**: 本地 CSV 文件
- **访问方式**: FileDataProvider
- **数据类型**: 历史价格、K线数据、技术指标

## 快速开始 / Quick Start

### 1. 生成样本数据 / Generate Sample Data

```bash
python generate_sample_data.py
```

这将在 `historical_data/` 目录下生成样本历史数据：
- `BTC_historical.csv`
- `ETH_historical.csv`
- `SOL_historical.csv`

### 2. 运行回测 / Run Backtest

**完整回测（需要 API Key）/ Full Backtest (requires API Key):**
```bash
python backtest_simulation.py
```

**简单回测（无需 API Key）/ Simple Backtest (no API Key needed):**
```bash
python simple_backtest_test.py
```

## 数据格式 / Data Format

历史数据 CSV 文件格式 / Historical data CSV file format:

```csv
timestamp,open,high,low,close,volume
1699999800,45000.0,45500.0,44800.0,45200.0,1234.56
1699999860,45200.0,45300.0,45000.0,45100.0,987.65
...
```

### 字段说明 / Field Descriptions

| 字段 / Field | 类型 / Type | 说明 / Description |
|-------------|------------|-------------------|
| timestamp | integer | Unix 时间戳（秒）/ Unix timestamp (seconds) |
| open | float | 开盘价 / Opening price |
| high | float | 最高价 / Highest price |
| low | float | 最低价 / Lowest price |
| close | float | 收盘价 / Closing price |
| volume | float | 成交量 / Trading volume |

## 自定义历史数据 / Custom Historical Data

### 准备您自己的数据 / Prepare Your Own Data

1. 创建 CSV 文件，文件名格式为 `{SYMBOL}_historical.csv`
2. 确保包含所有必需的列（timestamp, open, high, low, close, volume）
3. 将文件放在 `historical_data/` 目录下

示例 / Example:
```bash
# 创建自定义数据文件
historical_data/
  ├── BTC_historical.csv
  ├── ETH_historical.csv
  └── DOGE_historical.csv
```

### 从交易所下载历史数据 / Download from Exchange

您可以使用 CCXT 从交易所下载历史数据：

```python
import ccxt
import pandas as pd

exchange = ccxt.binance()
symbol = 'BTC/USDT'
timeframe = '3m'
since = exchange.parse8601('2023-01-01T00:00:00Z')

ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since)
df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = df['timestamp'] // 1000  # Convert to seconds
df.to_csv('historical_data/BTC_historical.csv', index=False)
```

## 回测配置 / Backtest Configuration

在 `backtest_simulation.py` 中可以修改以下配置：

```python
SYMBOLS = ['BTC', 'ETH', 'SOL']  # 交易对 / Trading symbols
UPDATE_FREQUENCY = '3m'           # 时间周期 / Time frequency
KLINE_COUNT = 10                  # K线数量 / Number of klines
DISPLAY_INTERVAL = 100            # 显示间隔 / Display interval
DATA_DIR = 'historical_data'      # 数据目录 / Data directory
```

## 回测结果 / Backtest Results

回测完成后，结果将保存到 `backtest_portfolio.json`，包含：
- 持仓信息 / Position information
- 盈亏统计 / P&L statistics
- 交易历史 / Trade history

示例输出 / Example output:
```
💰 Final Metrics:
  Initial Cash: $10,000.00
  Final Asset Value: $11,234.56
  Total Return: 12.35%
  Total PnL: $1,234.56
```

## 技术指标 / Technical Indicators

回测系统自动计算以下技术指标：
- RSI (7期和14期) / RSI (7-period and 14-period)
- MACD (12,26,9)
- EMA (20期和50期) / EMA (20-period and 50-period)
- ATR (3期和14期) / ATR (3-period and 14-period)

## 注意事项 / Important Notes

1. **数据质量** / Data Quality
   - 确保历史数据的质量和完整性
   - 避免使用有缺失值的数据

2. **回测偏差** / Backtesting Bias
   - 回测结果不代表未来表现
   - 注意过拟合问题
   - 考虑交易成本和滑点

3. **计算资源** / Computational Resources
   - 大量历史数据可能需要较长的处理时间
   - 建议从小数据集开始测试

4. **API Key** / API Key
   - 完整回测需要 AI API Key（OpenAI 或 OpenRouter）
   - 简单回测无需 API Key，仅验证数据加载和技术指标计算

## 故障排除 / Troubleshooting

### 问题：找不到数据文件
**错误**: `Data file not found: historical_data/BTC_historical.csv`

**解决方案**:
```bash
python generate_sample_data.py
```

### 问题：技术指标显示 NaN
**原因**: 数据点不足

**解决方案**: 确保至少有 50 个数据点用于计算 EMA-50

### 问题：回测运行缓慢
**解决方案**: 
- 减少 `KLINE_COUNT`
- 增加 `DISPLAY_INTERVAL`
- 使用更少的交易对

## 扩展 / Extensions

### 添加新的数据源
您可以创建自定义的 DataProvider：

```python
from data_provider import DataProvider

class CustomDataProvider(DataProvider):
    def get_last_price(self, symbol: str):
        # Your implementation
        pass
    
    def get_kline_data(self, symbol: str, period: str, count: int):
        # Your implementation
        pass
```

### 自定义交易策略
修改 `trade_decision_simple_AI.py` 中的策略逻辑，或创建新的决策提供者。

## 相关文件 / Related Files

- `backtest_simulation.py` - 完整回测脚本
- `simple_backtest_test.py` - 简单回测测试
- `data_provider.py` - 数据提供者抽象
- `generate_sample_data.py` - 样本数据生成器
- `test/test_data_provider.py` - 单元测试
