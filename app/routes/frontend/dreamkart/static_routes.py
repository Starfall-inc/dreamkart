from flask import jsonify, render_template, Blueprint

dreamkart_static_route_bp = Blueprint("dreamkart_static_routes",__name__)


@dreamkart_static_route_bp.route("/")
def dreamkart_home_page():
    """
    Home page for DreamKart SaaS platform.
    ---
    description: This route renders the home page of DreamKart, a multi-tenant e-commerce platform.
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
        return render_template("dreamkart/home/index.html")
    except Exception as e:
        return jsonify(e)
