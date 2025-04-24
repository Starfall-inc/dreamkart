# models/tenant.py
from app.extensions import db
from datetime import datetime

class Tenant(db.Model):
    """Tenant model - lives in the public schema."""
    __tablename__ = 'tenants'
    __table_args__ = {"schema": "public"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    schema_name = db.Column(db.String(63), unique=True, nullable=False)
    domain = db.Column(db.String(255), unique=True, nullable=False)
    subdomain = db.Column(db.String(63), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_email = db.Column(db.String(255), nullable=False)
    plan = db.Column(db.String(50), default='free')

    def __repr__(self):
        return f'<Tenant {self.name}>'

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "schema_name": self.schema_name,
            "domain": self.domain,
            "subdomain": self.subdomain,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "plan": self.plan
        }