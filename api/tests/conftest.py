"""Each integration test has a fresh public visitor budget."""
import pytest


@pytest.fixture(autouse=True)
def fresh_public_budget():
    from app.main import app
    from app.public_guard import PublicGuard
    middleware = app.middleware_stack
    while middleware is not None:
        if isinstance(middleware, PublicGuard):
            middleware.visitors.clear()
        middleware = getattr(middleware, 'app', None)
