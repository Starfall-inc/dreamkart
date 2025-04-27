# In your blueprint (e.g., store_routes.py or wherever you define these routes)
from flask import Blueprint, jsonify, render_template
from app.services.middleware import check_subdomain
from app.services.tenant import get_tenant_by_subdomain

dreamkart_static_route_bp = Blueprint("dreamkart_static_route", __name__)

@dreamkart_static_route_bp.route("/")
@check_subdomain
def home(subdomain=None):
    """
    Handles the homepage for both the main SaaS platform and store subdomains.
    ---
    description: Renders the appropriate homepage based on the presence of a subdomain.
    parameters:
      - name: subdomain
        in: path
        schema:
          type: string
        required: false
        description: The subdomain, if present in the request host.
    responses:
      200:
        description: Successfully rendered the appropriate homepage.
        content:
          text/html:
            examples:
              main_homepage: "<!DOCTYPE html>... (SaaS Homepage) ...</html>"
              store_homepage: "<!DOCTYPE html>... (Store Homepage for subdomain) ...</html>"
          application/json:
            examples:
              store_homepage_json: {"message": "Welcome to Store Home Page your_subdomain"}
      404:
        description: Tenant not found for the requested subdomain.
        content:
          application/json:
            example: {"error": "Tenant not found"}
      500:
        description: Internal server error.
        content:
          application/json:
            example: {"error": "An error occurred"}
    """
    if subdomain:
        return render_template("dreamkart/unclaimed_subdomain_landing.html", subdomain=subdomain)  # Replace with your actual template
    else:
        # This is the main SaaS platform's homepage logic
        try:
            return render_template("dreamkart/home/index.html")  # Replace with your actual template
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# Ensure you register this blueprint with your Flask app
# from app import app
# from app.routes.store_routes import store_bp
# app.register_blueprint(store_bp)