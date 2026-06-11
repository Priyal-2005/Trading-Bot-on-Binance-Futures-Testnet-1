# Binance Futures Testnet Trading Bot

A production-ready Python CLI trading bot for the **Binance Futures Testnet (USDT-M)**. Place **MARKET**, **LIMIT**, and **STOP_MARKET** orders from your terminal with full input validation, structured logging, and graceful error handling.

---

## Features

| Capability | Details |
|---|---|
| **Order Types** | MARKET · LIMIT · STOP_MARKET |
| **Sides** | BUY · SELL |
| **Input Validation** | Symbol, side, type, quantity, price, and stop-price rules enforced before any API call |
| **Structured Logging** | Timestamped file logs (`logs/trading.log`) for requests, responses, and errors |
| **Error Handling** | Custom exception hierarchy with specific classes for validation, API, network, and auth failures |
| **Clean Architecture** | Layered design — CLI → Service → Client — with strict separation of concerns |
| **Security** | API keys loaded from `.env`; never hard-coded |

---

## Architecture

```
┌─────────┐      ┌──────────────┐      ┌───────────────────────┐
│  cli.py │─────▶│ OrderService │─────▶│ BinanceFuturesClient  │──▶ Binance API
│ argparse│      │  (orders.py) │      │     (client.py)       │
└─────────┘      └──────────────┘      └───────────────────────┘
      │                                          ▲
      ▼                                          │
 validators.py                            exceptions.py
                                          logging_config.py
```

### Module Responsibilities

| Module | Role |
|---|---|
| `cli.py` | Parse CLI arguments, validate, invoke order service, print formatted output |
| `bot/orders.py` | Order service layer — prepare payload, dispatch to client, format response |
| `bot/client.py` | Binance Futures Testnet wrapper — initialise client, centralise API calls |
| `bot/validators.py` | Reusable, composable validation functions |
| `bot/logging_config.py` | File + console logging setup |
| `bot/exceptions.py` | Custom exception classes |

---

## Installation

### Prerequisites

- Python 3.11 or higher
- A [Binance Futures Testnet](https://testnet.binancefuture.com) account

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/trading_bot.git
cd trading_bot

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Binance Futures Testnet Setup

1. Navigate to [https://testnet.binancefuture.com](https://testnet.binancefuture.com).
2. Log in (or register) with a GitHub account.
3. Go to **API Management** and generate an API key pair.
4. Copy the **API Key** and **API Secret** — you will need them in the next step.

> **Note:** Testnet credentials are separate from your live Binance account. No real funds are at risk.

---

## Environment Configuration

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and paste your testnet credentials
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
```

> **Security:** `.env` is listed in `.gitignore` and will **never** be committed.

---

## Running Examples

### Example: MARKET Order

```bash
python cli.py \
  --symbol BTCUSDT \
  --side BUY \
  --type MARKET \
  --quantity 0.001
```

**Expected output:**

```
=== ORDER REQUEST ===
Symbol:     BTCUSDT
Side:       BUY
Type:       MARKET
Quantity:   0.001

=== ORDER RESPONSE ===
Order ID:      1234567890
Status:        FILLED
Executed Qty:  0.001
Average Price: 104230.50000000

Success: Order placed successfully
```

### Example: LIMIT Order

```bash
python cli.py \
  --symbol BTCUSDT \
  --side SELL \
  --type LIMIT \
  --quantity 0.001 \
  --price 100000
```

**Expected output:**

```
=== ORDER REQUEST ===
Symbol:     BTCUSDT
Side:       SELL
Type:       LIMIT
Quantity:   0.001
Price:      100000.0

=== ORDER RESPONSE ===
Order ID:      1234567891
Status:        NEW
Executed Qty:  0.000
Average Price: 0.00000000

Success: Order placed successfully
```

### Example: STOP_MARKET Order (Bonus)

```bash
python cli.py \
  --symbol BTCUSDT \
  --side BUY \
  --type STOP_MARKET \
  --quantity 0.001 \
  --stop-price 95000
```

**Expected output:**

```
=== ORDER REQUEST ===
Symbol:     BTCUSDT
Side:       BUY
Type:       STOP_MARKET
Quantity:   0.001
Stop Price: 95000.0

=== ORDER RESPONSE ===
Order ID:      1234567892
Status:        NEW
Executed Qty:  0.000
Average Price: 0.00000000

Success: Order placed successfully
```

---

## Logging Information

All activity is logged to **`logs/trading.log`** with the following format:

```
TIMESTAMP | LEVEL    | LOGGER               | MESSAGE
```

### Example Log Entries

#### Successful MARKET Order

```
2026-06-11 19:00:01 | INFO     | trading_bot.validators | All validations passed for BUY MARKET BTCUSDT order.
2026-06-11 19:00:01 | INFO     | trading_bot.orders     | Preparing BUY MARKET order for BTCUSDT — qty=0.001 price=None stopPrice=None
2026-06-11 19:00:01 | INFO     | trading_bot.client     | Placing MARKET order: symbol=BTCUSDT side=BUY quantity=0.001
2026-06-11 19:00:02 | INFO     | trading_bot.client     | Order response: {'orderId': 1234567890, 'status': 'FILLED', ...}
2026-06-11 19:00:02 | INFO     | trading_bot.orders     | Formatted order response: {'order_id': 1234567890, 'status': 'FILLED', ...}
```

#### Successful LIMIT Order

```
2026-06-11 19:01:01 | INFO     | trading_bot.validators | All validations passed for SELL LIMIT BTCUSDT order.
2026-06-11 19:01:01 | INFO     | trading_bot.orders     | Preparing SELL LIMIT order for BTCUSDT — qty=0.001 price=100000.0 stopPrice=None
2026-06-11 19:01:01 | INFO     | trading_bot.client     | Placing LIMIT order: symbol=BTCUSDT side=SELL quantity=0.001 price=100000.0
2026-06-11 19:01:02 | INFO     | trading_bot.client     | Order response: {'orderId': 1234567891, 'status': 'NEW', ...}
```

#### Successful STOP_MARKET Order

```
2026-06-11 19:02:01 | INFO     | trading_bot.validators | All validations passed for BUY STOP_MARKET BTCUSDT order.
2026-06-11 19:02:01 | INFO     | trading_bot.orders     | Preparing BUY STOP_MARKET order for BTCUSDT — qty=0.001 price=None stopPrice=95000.0
2026-06-11 19:02:01 | INFO     | trading_bot.client     | Placing STOP_MARKET order: symbol=BTCUSDT side=BUY quantity=0.001 stopPrice=95000.0
2026-06-11 19:02:02 | INFO     | trading_bot.client     | Order response: {'orderId': 1234567892, 'status': 'NEW', ...}
```

#### Validation Failure

```
2026-06-11 19:03:01 | ERROR    | trading_bot.validators | Quantity must be a positive number. Got: -1.
```

#### API Exception

```
2026-06-11 19:04:01 | ERROR    | trading_bot.client     | Binance API error [-1121]: Invalid symbol.
```

#### Network Exception

```
2026-06-11 19:05:01 | ERROR    | trading_bot.client     | Binance request error: Connection timed out.
```

---

## Assumptions

- The bot targets the **Binance Futures Testnet** only; it is **not** configured for live trading.
- Orders use the **USDT-M** (USD-margined) futures endpoint.
- `LIMIT` orders default to **GTC** (Good Till Cancelled) time-in-force.
- The `python-binance` library handles request signing and timestamp synchronisation.
- Users are expected to have an active testnet account with sufficient testnet balance.

---

## Future Improvements

- [ ] **OCO / bracket orders** — one-cancels-the-other for automated risk management
- [ ] **Position management** — query open positions, set leverage, change margin type
- [ ] **WebSocket streaming** — real-time price feeds and order status updates
- [ ] **Retry logic** — configurable exponential back-off on transient network errors
- [ ] **Unit & integration tests** — `pytest` test suite with mocked API responses
- [ ] **Docker support** — containerised deployment with `docker-compose`
- [ ] **Interactive mode** — REPL-style interface for rapid order entry
- [ ] **Configuration file** — YAML/TOML config for default symbols, quantities, and risk limits
- [ ] **Rate-limit awareness** — respect Binance API weight limits and queue requests

---

## License

This project is provided for **educational and testnet purposes only**. Use at your own risk.
