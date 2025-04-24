# middleware.py
from flask import g, request, abort
from app.services.tenant import get_tenant_by_domain, get_tenant_by_subdomain
import logging

logger = logging.getLogger(__name__)


def tenant_middleware():
    """Middleware to set the tenant schema based on domain."""
    # Skip tenant resolution for specific paths
    if request.path.startswith('/static') or request.path.startswith('/admin'):
        g.tenant_schema = 'public'
        return

    # Get domain from request
    host = request.host.split(':')[0]  # Remove port if present

    # Try to get tenant by full domain first
    tenant = get_tenant_by_domain(host)

    # If not found, try subdomain approach
    if not tenant:
        parts = host.split('.')
        if len(parts) > 2:  # It's a subdomain
            subdomain = parts[0]
            tenant = get_tenant_by_subdomain(subdomain)

    if tenant and tenant.is_active:
        g.tenant_schema = tenant.schema_name
        g.tenant = tenant
        logger.debug(f"Set tenant schema to {tenant.schema_name}")
    else:
        # Default to public schema - you might want to handle this differently
        g.tenant_schema = 'public'
        # For strict multi-tenancy, you might want to abort if no tenant found
        # abort(404, "Tenant not found")

    # Apply schema to session
    # This ensures new queries use the correct schema
    # Only needed if you're using raw SQL queries
    # For SQLAlchemy ORM queries, the Base model handles this
    if hasattr(g, 'tenant_schema'):
        from app.extensions import db
        if db.session:
            db.session.execute(f'SET search_path TO "{g.tenant_schema}"')


# Register in Flask app
def init_app(app):
    app.before_request(tenant_middleware)
