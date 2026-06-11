"""Binance Futures Testnet client wrapper.

Centralises all communication with the Binance API so the rest of the
application never imports ``binance`` directly.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from dotenv import load_dotenv

from bot.exceptions import APIConnectionError, AuthenticationError, OrderError

logger = logging.getLogger("trading_bot.client")

# Binance Futures Testnet base URL (must include the /fapi path)
_FUTURES_TESTNET_URL: str = "https://testnet.binancefuture.com/fapi"


class BinanceFuturesClient:
    """Thin wrapper around ``python-binance`` configured for the Futures Testnet.

    Usage::

        client = BinanceFuturesClient()
        response = client.create_market_order("BTCUSDT", "BUY", 0.001)
    """

    def __init__(self) -> None:
        """Initialise the Binance Futures Testnet client.

        Reads ``BINANCE_API_KEY`` and ``BINANCE_API_SECRET`` from the
        environment (loaded via *dotenv*) and configures the client to
        point at the Futures Testnet base URL.

        Raises:
            AuthenticationError: If the API key or secret is missing.
            APIConnectionError: If the initial connection to Binance fails.
        """
        load_dotenv()

        api_key: str | None = os.getenv("BINANCE_API_KEY")
        api_secret: str | None = os.getenv("BINANCE_API_SECRET")

        if not api_key or not api_secret:
            msg = (
                "BINANCE_API_KEY and BINANCE_API_SECRET must be set in the "
                "environment or in a .env file."
            )
            logger.error(msg)
            raise AuthenticationError(msg)

        try:
            self._client = Client(
                api_key=api_key,
                api_secret=api_secret,
                testnet=True,
            )
            # Override base URLs to point at the Futures Testnet
            self._client.FUTURES_URL = _FUTURES_TESTNET_URL
            logger.info("Binance Futures Testnet client initialised successfully.")
        except Exception as exc:
            msg = f"Failed to initialise Binance client: {exc}"
            logger.error(msg)
            raise APIConnectionError(msg) from exc

    # ------------------------------------------------------------------
    # Order methods
    # ------------------------------------------------------------------

    def create_market_order(
        self, symbol: str, side: str, quantity: float
    ) -> Dict[str, Any]:
        """Place a MARKET order on Binance Futures Testnet.

        Args:
            symbol: Trading pair (e.g. ``"BTCUSDT"``).
            side: ``"BUY"`` or ``"SELL"``.
            quantity: Order quantity.

        Returns:
            The raw API response dictionary.

        Raises:
            OrderError: On any Binance API or request error.
            APIConnectionError: On network-level failures.
        """
        logger.info(
            "Placing MARKET order: symbol=%s side=%s quantity=%s",
            symbol, side, quantity,
        )
        return self._execute_futures_order(
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity=str(quantity),
        )

    def create_limit_order(
        self, symbol: str, side: str, quantity: float, price: float
    ) -> Dict[str, Any]:
        """Place a LIMIT order on Binance Futures Testnet.

        Args:
            symbol: Trading pair.
            side: ``"BUY"`` or ``"SELL"``.
            quantity: Order quantity.
            price: Limit price.

        Returns:
            The raw API response dictionary.

        Raises:
            OrderError: On any Binance API or request error.
            APIConnectionError: On network-level failures.
        """
        logger.info(
            "Placing LIMIT order: symbol=%s side=%s quantity=%s price=%s",
            symbol, side, quantity, price,
        )
        return self._execute_futures_order(
            symbol=symbol,
            side=side,
            type="LIMIT",
            quantity=str(quantity),
            price=str(price),
            timeInForce="GTC",
        )

    def create_stop_market_order(
        self, symbol: str, side: str, quantity: float, stop_price: float
    ) -> Dict[str, Any]:
        """Place a STOP_MARKET order on Binance Futures Testnet.

        Args:
            symbol: Trading pair.
            side: ``"BUY"`` or ``"SELL"``.
            quantity: Order quantity.
            stop_price: Trigger / stop price.

        Returns:
            The raw API response dictionary.

        Raises:
            OrderError: On any Binance API or request error.
            APIConnectionError: On network-level failures.
        """
        logger.info(
            "Placing STOP_MARKET order: symbol=%s side=%s quantity=%s stopPrice=%s",
            symbol, side, quantity, stop_price,
        )
        return self._execute_futures_order(
            symbol=symbol,
            side=side,
            type="STOP_MARKET",
            quantity=str(quantity),
            stopPrice=str(stop_price),
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _execute_futures_order(self, **kwargs: Any) -> Dict[str, Any]:
        """Send a futures order to Binance and handle errors uniformly.

        Args:
            **kwargs: Keyword arguments forwarded to
                ``Client.futures_create_order``.

        Returns:
            The raw API response dictionary.

        Raises:
            OrderError: On ``BinanceAPIException``.
            APIConnectionError: On ``BinanceRequestException`` or other
                network errors.
        """
        try:
            response: Dict[str, Any] = self._client.futures_create_order(**kwargs)
            logger.info("Order response: %s", response)
            return response
        except BinanceAPIException as exc:
            msg = f"Binance API error [{exc.status_code}]: {exc.message}"
            logger.error(msg)
            raise OrderError(msg) from exc
        except BinanceRequestException as exc:
            msg = f"Binance request error: {exc}"
            logger.error(msg)
            raise APIConnectionError(msg) from exc
        except Exception as exc:
            msg = f"Unexpected error while placing order: {exc}"
            logger.error(msg)
            raise APIConnectionError(msg) from exc
