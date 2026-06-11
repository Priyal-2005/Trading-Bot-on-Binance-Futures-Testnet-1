"""Order service layer.

Sits between the CLI and the Binance client.  Responsible for preparing
the request payload, delegating to the correct client method, and
formatting the API response into a user-friendly dictionary.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from bot.client import BinanceFuturesClient

logger = logging.getLogger("trading_bot.orders")


class OrderService:
    """High-level service for placing and formatting futures orders.

    Usage::

        svc = OrderService()
        result = svc.place_order(
            symbol="BTCUSDT",
            side="BUY",
            order_type="MARKET",
            quantity=0.001,
        )
    """

    def __init__(self) -> None:
        """Create the service, initialising the underlying Binance client."""
        self._client = BinanceFuturesClient()
        logger.info("OrderService initialised.")

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Place an order and return a formatted response.

        Args:
            symbol: Trading pair (e.g. ``"BTCUSDT"``).
            side: ``"BUY"`` or ``"SELL"``.
            order_type: ``"MARKET"``, ``"LIMIT"``, or ``"STOP_MARKET"``.
            quantity: Positive order quantity.
            price: Required for ``LIMIT`` orders.
            stop_price: Required for ``STOP_MARKET`` orders.

        Returns:
            A dictionary with the keys ``order_id``, ``status``,
            ``executed_qty``, ``avg_price``, and ``raw_response``.
        """
        logger.info(
            "Preparing %s %s order for %s — qty=%s price=%s stopPrice=%s",
            side, order_type, symbol, quantity, price, stop_price,
        )

        raw: Dict[str, Any] = self._dispatch(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
        )

        formatted = self._format_response(raw)
        logger.info("Formatted order response: %s", formatted)
        return formatted

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _dispatch(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float],
        stop_price: Optional[float],
    ) -> Dict[str, Any]:
        """Route the order to the correct client method.

        Args:
            symbol: Trading pair.
            side: Order side.
            order_type: Order type.
            quantity: Order quantity.
            price: Limit price (may be ``None``).
            stop_price: Stop price (may be ``None``).

        Returns:
            The raw API response dictionary.
        """
        if order_type == "MARKET":
            return self._client.create_market_order(symbol, side, quantity)
        elif order_type == "LIMIT":
            # price is guaranteed non-None after validation
            return self._client.create_limit_order(symbol, side, quantity, price)  # type: ignore[arg-type]
        elif order_type == "STOP_MARKET":
            # stop_price is guaranteed non-None after validation
            return self._client.create_stop_market_order(symbol, side, quantity, stop_price)  # type: ignore[arg-type]
        else:
            # Should never happen after validation, but guard anyway.
            raise ValueError(f"Unsupported order type: {order_type}")

    @staticmethod
    def _format_response(raw: Dict[str, Any]) -> Dict[str, Any]:
        """Extract the most relevant fields from the raw API response.

        Args:
            raw: The raw Binance API response.

        Returns:
            A simplified dictionary for display purposes.
        """
        # Compute average price from fills when available
        avg_price: str = raw.get("avgPrice", "0")
        fills = raw.get("fills", [])
        if fills:
            total_cost = sum(float(f["price"]) * float(f["qty"]) for f in fills)
            total_qty = sum(float(f["qty"]) for f in fills)
            avg_price = f"{total_cost / total_qty:.8f}" if total_qty else avg_price

        return {
            "order_id": raw.get("orderId"),
            "status": raw.get("status"),
            "executed_qty": raw.get("executedQty", raw.get("origQty")),
            "avg_price": avg_price,
            "raw_response": raw,
        }
