"""Email module"""
from .service import EmailService, send_leave_request_notification, send_leave_request_approved, send_leave_request_rejected

__all__ = [
    "EmailService",
    "send_leave_request_notification",
    "send_leave_request_approved",
    "send_leave_request_rejected"
]
