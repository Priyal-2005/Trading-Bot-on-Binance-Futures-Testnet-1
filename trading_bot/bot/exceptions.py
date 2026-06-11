"""Custom exception classes for the trading bot."""


class TradingBotError(Exception):
    """Base exception for all trading bot errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class ValidationError(TradingBotError):
    """Raised when input validation fails."""

    def __init__(self, message: str) -> None:
        super().__init__(f"Validation Error: {message}")


class OrderError(TradingBotError):
    """Raised when an order placement fails."""

    def __init__(self, message: str) -> None:
        super().__init__(f"Order Error: {message}")


class APIConnectionError(TradingBotError):
    """Raised when the API connection fails or times out."""

    def __init__(self, message: str) -> None:
        super().__init__(f"API Connection Error: {message}")


class AuthenticationError(TradingBotError):
    """Raised when API key authentication fails."""

    def __init__(self, message: str) -> None:
        super().__init__(f"Authentication Error: {message}")
