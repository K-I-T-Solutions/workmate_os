"""
WorkmateOS Error Handling

Zentrales Error Management System für konsistente, benutzerfreundliche Fehlermeldungen.
"""

from .messages import ErrorCode, ErrorMessage, get_error_detail

__all__ = ["ErrorCode", "ErrorMessage", "get_error_detail"]
