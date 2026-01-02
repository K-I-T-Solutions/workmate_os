"""
Dependencies für Invoice Routes
"""
from typing import Optional
from fastapi import Request


def get_request_context(request: Request) -> dict:
    """
    Extrahiert Kontext-Informationen aus dem Request.
    
    Returns:
        dict mit user_id und ip_address
    """
    # User-ID aus Request-State (wird von Auth-Middleware gesetzt)
    user_id = getattr(request.state, "user_id", None)
    
    # IP-Adresse aus verschiedenen Headers (hinter Proxy)
    ip_address = (
        request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        or request.headers.get("X-Real-IP")
        or (request.client.host if request.client else None)
    )
    
    return {
        "user_id": user_id,
        "ip_address": ip_address
    }


class RequestContext:
    """
    Request-Context als Injectable Dependency.
    """
    def __init__(self, request: Request):
        self.user_id: Optional[str] = getattr(request.state, "user_id", None)
        
        # IP-Adresse aus verschiedenen Headers
        forwarded_for = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        real_ip = request.headers.get("X-Real-IP")
        client_ip = request.client.host if request.client else None
        
        self.ip_address: Optional[str] = forwarded_for or real_ip or client_ip
