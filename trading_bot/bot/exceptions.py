"""Custom exception classes for the trading bot.

Hierarchy::

    TradingBotError (base)
    ├── ValidationError
    ├── OrderError
    ├── APIConnectionError
    └── AuthenticationError
"""


class TradingBotError(Exception):
    """Base exception for all trading bot errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class ValidationError(TradingBotError):
    """Raised when input validation fails."""


class OrderError(TradingBotError):
    """Raised when an order placement fails."""


class APIConnectionError(TradingBotError):
    """Raised when the API connection fails or times out."""


class AuthenticationError(TradingBotError):
    """Raised when API key authentication fails."""
