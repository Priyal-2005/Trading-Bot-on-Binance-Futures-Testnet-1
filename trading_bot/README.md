# Binance Futures Testnet Trading Bot

A Python CLI trading bot for the **Binance Futures Testnet (USDT-M)**. Place **MARKET**, **LIMIT**, and **STOP_MARKET** orders from your terminal with full input validation, structured logging, and graceful error handling.

---

## Features

| Capability | Details |
|---|---|
| **Order Types** | MARKET · LIMIT · STOP_MARKET |
| **Sides** | BUY · SELL |
| **Input Validation** | Symbol normalization (uppercase, trimmed), numeric checks, type-specific rules — all enforced before any API call |
| **Structured Logging** | Timestamped file logs (`logs/trading.log`) for requests, responses, and errors |
| **Error Handling** | Custom exception hierarchy with specific classes for validation, API, network, and auth failures |
| **Clean Architecture** | Layered design — CLI → Service → Client — with strict separation of concerns |
| **Security** | API keys loaded from `.env`; never hard-coded |

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py          # Package marker
│   ├── client.py            # Binance Futures Testnet API wrapper
│   ├── orders.py            # Order service layer (dispatch + format)
│   ├── validators.py        # Input validation and symbol normalization
│   ├── exceptions.py        # Custom exception hierarchy
│   └── logging_config.py    # File + console logging setup
├── logs/
│   ├── .gitkeep             # Keeps the directory in git
│   ├── market_order.log     # Example: MARKET BUY execution log
│   └── limit_order.log      # Example: LIMIT SELL execution log
├── cli.py                   # CLI entry-point (argparse)
├── README.md
├── requirements.txt         # Pinned dependencies
├── .env.example             # Template for API credentials
├── .gitignore
└── LICENSE                  # MIT License
```

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
| `bot/validators.py` | Reusable validation functions with symbol normalization |
| `bot/logging_config.py` | File + console logging setup |
| `bot/exceptions.py` | Custom exception hierarchy (`TradingBotError` base → `ValidationError`, `OrderError`, `APIConnectionError`, `AuthenticationError`) |

---

## Installation

### Prerequisites

- Python 3.10 or higher
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
Order ID:      4196469069
Status:        FILLED
Executed Qty:  0.001
Average Price: 104237.50000

Success: Order placed successfully
```

### Example: LIMIT Order

```bash
python cli.py \
  --symbol BTCUSDT \
  --side SELL \
  --type LIMIT \
  --quantity 0.001 \
  --price 110000
```

**Expected output:**

```
=== ORDER REQUEST ===
Symbol:     BTCUSDT
Side:       SELL
Type:       LIMIT
Quantity:   0.001
Price:      110000.0

=== ORDER RESPONSE ===
Order ID:      4196469073
Status:        NEW
Executed Qty:  0.000
Average Price: 0.00000

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
Order ID:      4196469078
Status:        NEW
Executed Qty:  0.000
Average Price: 0.00000

Success: Order placed successfully
```

---

## Logging Information

All activity is logged to **`logs/trading.log`** with the following format:

```
TIMESTAMP | LEVEL    | LOGGER               | MESSAGE
```

- **File handler** — logs at `INFO` level and above to `logs/trading.log`.
- **Console handler** — logs at `WARNING` level and above to stderr (avoids cluttering CLI output).

### Example Log Entries

#### Successful MARKET Order

```
2026-06-11 19:15:01 | INFO     | trading_bot.validators | All validations passed for BUY MARKET BTCUSDT order.
2026-06-11 19:15:01 | INFO     | trading_bot.orders   | Preparing BUY MARKET order for BTCUSDT — qty=0.001 price=None stopPrice=None
2026-06-11 19:15:01 | INFO     | trading_bot.client   | Placing MARKET order: symbol=BTCUSDT side=BUY quantity=0.001
2026-06-11 19:15:02 | INFO     | trading_bot.client   | Order response: {'orderId': 4196469069, 'status': 'FILLED', ...}
2026-06-11 19:15:02 | INFO     | trading_bot.orders   | Formatted order response: {'order_id': 4196469069, 'status': 'FILLED', ...}
```

#### Successful LIMIT Order

```
2026-06-11 19:16:01 | INFO     | trading_bot.validators | All validations passed for SELL LIMIT BTCUSDT order.
2026-06-11 19:16:01 | INFO     | trading_bot.orders   | Preparing SELL LIMIT order for BTCUSDT — qty=0.001 price=110000.0 stopPrice=None
2026-06-11 19:16:01 | INFO     | trading_bot.client   | Placing LIMIT order: symbol=BTCUSDT side=SELL quantity=0.001 price=110000.0
2026-06-11 19:16:02 | INFO     | trading_bot.client   | Order response: {'orderId': 4196469073, 'status': 'NEW', ...}
```

#### Validation Failure

```
2026-06-11 19:03:01 | ERROR    | trading_bot.validators | Quantity must be a finite positive number. Got: -1.
```

#### API Exception

```
2026-06-11 19:04:01 | ERROR    | trading_bot.client     | Binance API error [-1121]: Invalid symbol.
```

#### Network Exception

```
2026-06-11 19:05:01 | ERROR    | trading_bot.client     | Binance request error: Connection timed out.
```

> **Tip:** Example log files are included in the `logs/` directory — see `market_order.log` and `limit_order.log`.

---

## Screenshots

*Screenshots of actual terminal execution will be added here after running against the Binance Futures Testnet.*

<!-- TODO: Add terminal screenshots showing:
  1. A successful MARKET order
  2. A successful LIMIT order
  3. A validation error example
-->

---

## Troubleshooting

### `AuthenticationError: BINANCE_API_KEY and BINANCE_API_SECRET must be set`

**Cause:** The `.env` file is missing or the API credentials are not set.

**Fix:**
```bash
cp .env.example .env
# Edit .env and paste your testnet API key and secret
```

### `BinanceAPIException: APIError(code=-1021): Timestamp for this request was 1000ms ahead`

**Cause:** Your system clock is out of sync with Binance servers.

**Fix:**
```bash
# macOS
sudo sntp -sS time.apple.com

# Linux
sudo ntpdate -s time.nist.gov
```

### `BinanceAPIException: APIError(code=-2019): Margin is insufficient`

**Cause:** The testnet account does not have enough USDT balance.

**Fix:** Testnet balances are reset periodically (usually monthly). Log in to [testnet.binancefuture.com](https://testnet.binancefuture.com) and check your balance. If it's zero, wait for the next reset or create a new testnet account.

### `ModuleNotFoundError: No module named 'binance'`

**Cause:** Dependencies are not installed.

**Fix:**
```bash
pip install -r requirements.txt
```

### `ConnectionError` or `BinanceRequestException`

**Cause:** Network issue or Binance Testnet is temporarily down.

**Fix:** Check your internet connection. The testnet may have occasional downtime — retry after a few minutes.

---

## Common Binance API Errors

| Error Code | Message | Cause | Fix |
|---|---|---|---|
| `-1121` | Invalid symbol | Symbol doesn't exist (e.g. `BTCUSD` instead of `BTCUSDT`) | Use a valid USDT-M futures pair |
| `-1102` | Mandatory parameter missing | Required parameter not sent | Check order type requirements (price for LIMIT, stopPrice for STOP_MARKET) |
| `-2019` | Margin is insufficient | Not enough testnet USDT | Wait for testnet balance reset |
| `-1021` | Timestamp outside recvWindow | System clock drift | Sync system clock (see Troubleshooting) |
| `-4003` | Quantity less than minimum | Order quantity below minimum allowed | Check symbol's minimum quantity (e.g. 0.001 for BTCUSDT) |
| `-4014` | Price not increased by tick size | Price doesn't match tick size | Round to the symbol's price precision |

---

## Assumptions

- The bot targets the **Binance Futures Testnet** only; it is **not** configured for live trading.
- Orders use the **USDT-M** (USD-margined) futures endpoint.
- `LIMIT` orders default to **GTC** (Good Till Cancelled) time-in-force.
- The `python-binance` library handles request signing and timestamp synchronisation.
- Users are expected to have an active testnet account with sufficient testnet balance.
- Symbols are automatically normalized to uppercase (e.g. `btcusdt` → `BTCUSDT`).

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

This project is licensed under the [MIT License](LICENSE).
