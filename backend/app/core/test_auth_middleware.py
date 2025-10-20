# app/core/test_auth_middleware.py
import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class TestAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware für automatisierte Tests.
    Liest X-Test-User Header und setzt request.state.test_user.
    """
    async def dispatch(self, request: Request, call_next):
        test_user_header = request.headers.get("X-Test-User")
        if test_user_header:
            try:
                request.state.test_user = json.loads(test_user_header)
            except json.JSONDecodeError:
                request.state.test_user = None
        response = await call_next(request)
        return response
