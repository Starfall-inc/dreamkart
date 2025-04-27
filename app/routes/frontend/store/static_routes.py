from flask import Blueprint
from app.services.tenant import get_tenant_by_subdomain
from app.services.middleware import check_subdomain

store_static_route_bp = Blueprint("store_static_routes", __name__)

@store_static_route_bp.route("/")
@check_subdomain
def store_home_page(subdomain=None):
    """
    Home page for Store SaaS platform.
    ---
    description: This route renders the home page of Store, a multi-tenant e-commerce platform.
    Responses:
      200:
        description: Successfully rendered the home page template
        content:
          text/html:
            example: "<!DOCTYPE html>...</html>"
      500:
        description: Internal server error
        content:
          application/json:
            example: {"error": "An error occurred"}
    """
    try:
        return jsonify(f"Welcome to Store Home Page {subdomain}")
    except Exception as e:
        return jsonify(e)