# models/base.py
from app.extensions import db
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID


class SchemaBaseModel:
    """Base class for all models with dynamic schema support."""

    @declared_attr
    def __tablename__(cls):
        # Convert CamelCase to snake_case for table names
        name = cls.__name__
        return ''.join(['_' + c.lower() if c.isupper() else c for c in name]).lstrip('_')

    @declared_attr
    def __table_args__(cls):
        return {'schema': cls.get_schema()}

    @classmethod
    def get_schema(cls):
        from flask import g
        # Get current tenant schema from Flask g object or a default
        return getattr(g, 'tenant_schema', 'public')


class Base(SchemaBaseModel, db.Model):
    """Abstract base model with common attributes."""
    __abstract__ = True

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def soft_delete(self):
        """Mark record as deleted without removing from database."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        return self
