from app.routes.frontend.dreamkart.static_routes import dreamkart_static_route_bp


def register_blueprints(app):
    app.register_blueprint(dreamkart_static_route_bp, url_prefix="/")
