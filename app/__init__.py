# app/__init__.py
import os
from flask import Flask, g
from flask_migrate import Migrate
from flask_cors import CORS
from app.routes import register_blueprints

from app.extensions import db
from app.utils.tenant_utils import get_tenant_schema


def create_app(config_class=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Load configuration
    if config_class is None:
        # Default to using environment variable
        config_name = os.environ.get('FLASK_CONFIG', 'development')
        app.config.from_object(f'app.config.{config_name.capitalize()}Config')
    else:
        # Use provided config class
        app.config.from_object(config_class)

    # Initialize extensions
    init_extensions(app)

    # Register blueprints
    register_blueprints(app)

    # Configure tenant handling
    setup_tenant_handling(app)

    # Enable CORS if configured
    if app.config.get('ENABLE_CORS', False):
        CORS(app, resources={r"/api/*": {"origins": app.config.get('CORS_ORIGINS', '*')}})

    # Register error handlers
    register_error_handlers(app)

    @app.context_processor
    def inject_jinja():
        return {
            "DOMAIN_NAME" : app.config.get("DOMAIN")
        }

    return app


def init_extensions(app):
    """Initialize Flask extensions."""
    # Initialize SQLAlchemy
    db.init_app(app)

    # Initialize Flask-Migrate
    Migrate(app, db)

    # Import your models here!
    from app.models.tenant import Tenant

    # Initialize other extensions here


def setup_tenant_handling(app):
    """Configure multi-tenant schema handling."""

    @app.before_request
    def set_tenant_schema():
        # Set tenant schema in Flask g object
        g.tenant_schema = get_tenant_schema()


def register_error_handlers(app):
    """Register error handlers."""

    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Resource not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500
