#!/usr/bin/env python3
"""Command-line interface for the Binance Futures Testnet trading bot.

Usage examples::

    # MARKET order
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

    # LIMIT order
    python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 100000

    # STOP_MARKET order
    python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 95000
"""

from __future__ import annotations

import argparse
import sys
from typing import Any, Dict

from bot.exceptions import TradingBotError
from bot.logging_config import setup_logging
from bot.orders import OrderService
from bot.validators import validate_order_params




# ------------------------------------------------------------------
# CLI argument parsing
# ------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    """Build and return the ``argparse`` argument parser.

    Returns:
        argparse.ArgumentParser: Configured parser for order arguments.
    """
    parser = argparse.ArgumentParser(
        description="Binance Futures Testnet Trading Bot — place MARKET, LIMIT, and STOP_MARKET orders.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001\n"
            "  python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 100000\n"
            "  python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 95000\n"
        ),
    )

    parser.add_argument(
        "--symbol",
        type=str,
        required=True,
        help="Trading pair symbol (e.g. BTCUSDT).",
    )
    parser.add_argument(
        "--side",
        type=str,
        required=True,
        choices=["BUY", "SELL"],
        help="Order side: BUY or SELL.",
    )
    parser.add_argument(
        "--type",
        type=str,
        required=True,
        dest="order_type",
        choices=["MARKET", "LIMIT", "STOP_MARKET"],
        help="Order type: MARKET, LIMIT, or STOP_MARKET.",
    )
    parser.add_argument(
        "--quantity",
        type=float,
        required=True,
        help="Order quantity (must be positive).",
    )
    parser.add_argument(
        "--price",
        type=float,
        default=None,
        help="Limit price (required for LIMIT orders).",
    )
    parser.add_argument(
        "--stop-price",
        type=float,
        default=None,
        dest="stop_price",
        help="Stop / trigger price (required for STOP_MARKET orders).",
    )

    return parser


# ------------------------------------------------------------------
# Display helpers
# ------------------------------------------------------------------

def _print_order_request(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float | None = None,
    stop_price: float | None = None,
) -> None:
    """Print a formatted order-request summary to stdout.

    Args:
        symbol: Trading pair.
        side: Order side.
        order_type: Order type.
        quantity: Order quantity.
        price: Limit price (optional).
        stop_price: Stop price (optional).
    """
    print("\n=== ORDER REQUEST ===")
    print(f"Symbol:     {symbol}")
    print(f"Side:       {side}")
    print(f"Type:       {order_type}")
    print(f"Quantity:   {quantity}")
    if price is not None:
        print(f"Price:      {price}")
    if stop_price is not None:
        print(f"Stop Price: {stop_price}")
    print()


def _print_order_response(result: Dict[str, Any]) -> None:
    """Print a formatted order-response summary to stdout.

    Args:
        result: The formatted response from ``OrderService.place_order``.
    """
    print("=== ORDER RESPONSE ===")
    print(f"Order ID:      {result['order_id']}")
    print(f"Status:        {result['status']}")
    print(f"Executed Qty:  {result['executed_qty']}")
    print(f"Average Price: {result['avg_price']}")
    print()
    print("Success: Order placed successfully")


# ------------------------------------------------------------------
# Main entry-point
# ------------------------------------------------------------------

def main() -> None:
    """Parse CLI arguments, validate, and place the order."""
    logger = setup_logging()
    parser = _build_parser()
    args = parser.parse_args()

    try:
        # --- Validate ---
        validate_order_params(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )

        # --- Display request ---
        _print_order_request(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )

        # --- Place order ---
        service = OrderService()
        result = service.place_order(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )

        # --- Display response ---
        _print_order_response(result)

    except TradingBotError as exc:
        logger.error("Trading bot error: %s", exc.message)
        print(f"\nError: {exc.message}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(130)
    except Exception as exc:
        logger.exception("Unhandled exception: %s", exc)
        print(f"\nError: An unexpected error occurred — {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
