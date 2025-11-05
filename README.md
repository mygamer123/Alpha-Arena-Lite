# Alpha-Arena-Lite

加密货币交易模拟平台

作者：Moshi Wei

这可能是全网最简单的Alpha Arena 复刻了，非常方便小白快速上手体验AI炒股，请猛猛加星🌟

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

在项目根目录创建 `.env` 文件，添加你的 API Key：

**使用 OpenAI (推荐 - 默认使用 DeepSeek):**
```env
OPENAI_API_KEY=sk-your-api-key-here
```

**或者使用 OpenRouter (支持多种 AI 模型):**
```env
OPENROUTER_API_KEY=sk-or-your-api-key-here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
```

OpenRouter 支持的模型包括：
- `anthropic/claude-3.5-sonnet` - Claude 3.5 Sonnet
- `openai/gpt-4` - GPT-4
- `google/gemini-pro` - Gemini Pro
- 更多模型请访问：https://openrouter.ai/models

### 3. 运行模拟

```bash
python simulation.py
```

就这么简单！🎉

## 说明

- 模拟会自动从 `portfolio_init.json` 加载初始投资组合配置
- 如果没有找到 `portfolio_init.json`，会创建一个新的投资组合
- 运行状态会保存到 `portfolio.json`

---

## 数据源说明

### 实时价格数据源
本项目使用 **Hyperliquid** 交易所作为加密货币实时价格数据源，通过 CCXT 库进行访问。

- **交易所**: Hyperliquid
- **访问方式**: CCXT (CryptoCurrency eXchange Trading Library)
- **支持的币种**: BTC, ETH, SOL, DOGE, BNB, XRP 等主流加密货币
- **数据类型**: 
  - 实时价格
  - K线数据（支持多种时间周期：1m, 3m, 5m, 15m, 30m, 1h, 4h, 1d）
  - 技术指标（RSI, MACD, EMA, ATR 等）

详见 `hyperliquid_market_data.py` 文件。

### 回测功能
除了实时交易模拟，本项目还支持使用本地历史数据进行回测：

```bash
python backtest_simulation.py
```

回测功能使用本地 CSV 文件作为历史数据源，无需连接实时交易所，适合：
- 策略验证
- 历史数据分析
- 离线测试

详见下方"回测模式"部分或查看 [回测功能详细指南](BACKTEST_GUIDE.md)。

## 回测模式

### 准备历史数据

首先生成样本数据：
```bash
python generate_sample_data.py
```

或在 `historical_data/` 目录下放置自己的 CSV 格式历史数据文件，文件名格式为 `{SYMBOL}_historical.csv`。

CSV 文件格式：
```csv
timestamp,open,high,low,close,volume
1699999800,45000.0,45500.0,44800.0,45200.0,1234.56
1699999860,45200.0,45300.0,45000.0,45100.0,987.65
```

### 运行回测

```bash
python backtest_simulation.py
```

回测模式会：
1. 从本地文件加载历史数据
2. 按时间顺序模拟交易
3. 生成交易决策
4. 记录回测结果到 `backtest_portfolio.json`

## 注意事项

- 确保已安装所有 `requirements.txt` 中的依赖包
- 需要有效的 OpenAI API Key 或 OpenRouter API Key 才能使用 AI 交易决策功能
- 如果同时配置了 OpenRouter 和 OpenAI，系统会优先使用 OpenRouter
- 首次运行前建议检查 `portfolio_init.json` 配置是否符合需求
- 回测模式需要在 `historical_data/` 目录准备相应的历史数据文件

讨论群链接：
![Alpha Arena Lite](image.png)