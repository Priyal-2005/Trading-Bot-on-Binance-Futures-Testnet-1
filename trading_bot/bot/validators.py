"""Reusable validation functions for CLI inputs and order parameters.

Every public function raises ``ValidationError`` on invalid input and
returns ``None`` on success, keeping the call-site pattern simple:

    validate_symbol(symbol)   # raises or passes silently
"""

from __future__ import annotations

import logging
import math
from typing import Optional

from bot.exceptions import ValidationError

logger = logging.getLogger("trading_bot.validators")

VALID_SIDES: tuple[str, ...] = ("BUY", "SELL")
VALID_ORDER_TYPES: tuple[str, ...] = ("LIMIT", "MARKET", "STOP_MARKET")


def validate_symbol(symbol: Optional[str]) -> None:
    """Validate that *symbol* is a non-empty string.

    Args:
        symbol: The trading pair symbol (e.g. ``"BTCUSDT"``).

    Raises:
        ValidationError: If *symbol* is ``None`` or blank.
    """
    if not symbol or not symbol.strip():
        msg = "Symbol is required and cannot be empty."
        logger.error(msg)
        raise ValidationError(msg)


def validate_side(side: Optional[str]) -> None:
    """Validate that *side* is either ``BUY`` or ``SELL``.

    Args:
        side: The order side.

    Raises:
        ValidationError: If *side* is not one of the allowed values.
    """
    if side not in VALID_SIDES:
        msg = f"Side must be one of {VALID_SIDES}. Got: '{side}'."
        logger.error(msg)
        raise ValidationError(msg)


def validate_order_type(order_type: Optional[str]) -> None:
    """Validate that *order_type* is ``MARKET``, ``LIMIT``, or ``STOP_MARKET``.

    Args:
        order_type: The order type string.

    Raises:
        ValidationError: If *order_type* is not one of the allowed values.
    """
    if order_type not in VALID_ORDER_TYPES:
        msg = f"Order type must be one of {VALID_ORDER_TYPES}. Got: '{order_type}'."
        logger.error(msg)
        raise ValidationError(msg)


def validate_quantity(quantity: Optional[float]) -> None:
    """Validate that *quantity* is a positive number.

    Args:
        quantity: The order quantity.

    Raises:
        ValidationError: If *quantity* is ``None``, zero, or negative.
    """
    if quantity is None or not math.isfinite(quantity) or quantity <= 0:
        msg = f"Quantity must be a finite positive number. Got: {quantity}."
        logger.error(msg)
        raise ValidationError(msg)


def validate_price(price: Optional[float], order_type: str) -> None:
    """Validate that *price* is positive when required by *order_type*.

    ``LIMIT`` orders **must** include a positive price.

    Args:
        price: The limit price.
        order_type: The order type (used to decide if price is mandatory).

    Raises:
        ValidationError: If a ``LIMIT`` order has no price or a non-positive
            price.
    """
    if order_type == "LIMIT":
        if price is None or not math.isfinite(price) or price <= 0:
            msg = f"LIMIT orders require a finite positive price. Got: {price}."
            logger.error(msg)
            raise ValidationError(msg)


def validate_stop_price(stop_price: Optional[float], order_type: str) -> None:
    """Validate that *stop_price* is positive when required by *order_type*.

    ``STOP_MARKET`` orders **must** include a positive stop price.

    Args:
        stop_price: The stop/trigger price.
        order_type: The order type.

    Raises:
        ValidationError: If a ``STOP_MARKET`` order has no stop price or a
            non-positive stop price.
    """
    if order_type == "STOP_MARKET":
        if stop_price is None or not math.isfinite(stop_price) or stop_price <= 0:
            msg = f"STOP_MARKET orders require a finite positive stop price. Got: {stop_price}."
            logger.error(msg)
            raise ValidationError(msg)


def validate_order_params(
    symbol: Optional[str],
    side: Optional[str],
    order_type: Optional[str],
    quantity: Optional[float],
    price: Optional[float] = None,
    stop_price: Optional[float] = None,
) -> None:
    """Run **all** validations for an order in a single call.

    This is the main entry-point used by the CLI and the order service.

    Args:
        symbol: Trading pair.
        side: ``"BUY"`` or ``"SELL"``.
        order_type: ``"MARKET"``, ``"LIMIT"``, or ``"STOP_MARKET"``.
        quantity: Positive order quantity.
        price: Required for ``LIMIT`` orders.
        stop_price: Required for ``STOP_MARKET`` orders.

    Raises:
        ValidationError: On the first validation that fails.
    """
    validate_symbol(symbol)
    validate_side(side)
    validate_order_type(order_type)
    validate_quantity(quantity)
    validate_price(price, order_type)
    validate_stop_price(stop_price, order_type)
    logger.info("All validations passed for %s %s %s order.", side, order_type, symbol)
