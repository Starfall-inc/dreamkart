# app/utils/tenant_utils.py
from flask import request, current_app

def get_tenant_schema():
    """
    Extract tenant schema from request.

    The schema can be determined from:
    1. X-Tenant-ID header
    2. subdomain
    3. query parameter
    """
    # Try to get from header first
    tenant_id = request.headers.get('X-Tenant-ID')

    # If not in header, try to extract from subdomain
    if not tenant_id:
        host = request.host.split(':')[0]  # Remove port if present
        parts = host.split('.')
        if len(parts) > 2:  # Subdomain exists
            tenant_id = parts[0]

    # If still not found, try query param
    if not tenant_id:
        tenant_id = request.args.get('tenant')

    # Use default if tenant not determined
    if not tenant_id:
        return current_app.config.get('DEFAULT_SCHEMA', 'public')

    # Sanitize schema name (allow only alphanumeric and underscore)
    import re
    tenant_id = re.sub(r'[^a-zA-Z0-9_]', '', tenant_id).lower()

    return tenant_id