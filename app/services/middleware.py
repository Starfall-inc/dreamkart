# middleware.py
from functools import wraps
from flask import request, g, abort
from app.services.tenant import get_tenant_by_subdomain
import logging

logger = logging.getLogger(__name__)

def check_subdomain(route_func):
    """
    A decorator for Flask routes that extracts the subdomain and passes it as an argument.

    It checks if the request host has more than two parts (indicating a subdomain).
    If so, it extracts the first part as the subdomain and makes it available
    as an argument to the decorated route function.

    If no subdomain is present (e.g., the request is on the main domain),
    the route function will be called without the subdomain argument.

    Note: This decorator should be applied *after* any route-specific decorators
    (like @app.route('/some/path')).
    """
    @wraps(route_func)
    def decorated_route(*args, **kwargs):
        host = request.host.split(':')[0]  # Remove port if present
        parts = host.split('.')
        subdomain = None

        if len(parts) > 2:
            subdomain = parts[0]
            logger.debug(f"Extracted subdomain: {subdomain}")
            return route_func(subdomain=subdomain, *args, **kwargs)
        else:
            logger.debug("No subdomain found for this request.")
            return route_func(*args, **kwargs)
    return decorated_route

# Example of how to use it in your Flask app:
# from app import app
# from middleware import check_subdomain
#
# @app.route('/')
# @check_subdomain
# def index(subdomain=None):
#     if subdomain:
#         return f"Welcome to the subdomain: {subdomain}"
#     else:
#         return "Welcome to the main domain!"
#
# @app.route('/profile')
# @check_subdomain
# def profile(subdomain=None):
#     if subdomain:
#         # Access tenant information based on the subdomain
#         tenant = get_tenant_by_subdomain(subdomain)
#         if tenant:
#             return f"Profile for tenant: {tenant.name} (subdomain: {subdomain})"
#         else:
#             abort(404, "Tenant not found for this subdomain")
#     else:
#         return "Your profile on the main domain."

# You would typically apply this decorator to your route functions directly.
# The `init_app` function you had before for `before_request` middleware
# is still relevant for setting the tenant based on the subdomain (as you were doing).
# You might want to keep that `tenant_middleware` as a `before_request`
# to ensure `g.tenant_schema` is set for database operations.

def init_app(app):
    # Keep your existing tenant middleware to set g.tenant_schema
    app.before_request(tenant_middleware)
    # The new `check_subdomain` is used as a decorator on individual routes.
    pass