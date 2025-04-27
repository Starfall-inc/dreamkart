# app/config.py
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class BaseConfig:
    """Base configuration."""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-please-change-in-production')
    DEBUG = False
    TESTING = False

    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'postgresql://postgres:postgres@localhost:5432/myapp')

    # MinIO Storage
    MINIO_ENDPOINT = os.environ.get('MINIO_ENDPOINT', 'localhost:9000')
    MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY', 'minioadmin')
    MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY', 'minioadmin')
    MINIO_SECURE = os.environ.get('MINIO_SECURE', 'False').lower() == 'true'
    MINIO_PUBLIC_URL = os.environ.get('MINIO_PUBLIC_URL', None)

    # Jinja Context Processors
    DOMAIN = os.environ.get('DOMAIN', 'localhost:5000')

    # CORS
    ENABLE_CORS = True
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')

    # Default tenant schema
    DEFAULT_SCHEMA = 'public'


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class TestingConfig(BaseConfig):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # temporary DB for testing
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(BaseConfig):
    """Production configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Must be set in environment
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')  # Must be set in environment

    # MinIO settings
    MINIO_SECURE = True

    # Security settings
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True