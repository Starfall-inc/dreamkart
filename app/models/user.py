# models/user.py
from app.models.base import Base, db
from datetime import datetime


class User(Base):
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15))
    password = db.Column(db.String(255))
    default_location = db.Column(db.String(255))
    role = db.Column(db.String(20), default='customer')
    status = db.Column(db.String(20), default='active')
    auth_provider = db.Column(
        db.Enum('google', 'manual', name='auth_provider_enum'),
        server_default='manual'
    )
    profile_pic_url = db.Column(db.String(255), default='none')

    # Relationships
    orders = db.relationship('Order', back_populates='user', lazy=True)
    reviews = db.relationship('ProductReview', back_populates='user', lazy=True, cascade='all, delete-orphan')
    carts = db.relationship('ShoppingCart', back_populates='user', lazy=True)
    sessions = db.relationship('Session', back_populates='user', lazy=True, cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('email', name='unique_user_email'),
        {'schema': Base.get_schema()}
    )

    def __repr__(self):
        return f'<User {self.email}>'

    def to_dict(self, include_sensitive=False):
        data = {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "default_location": self.default_location,
            "role": self.role,
            "status": self.status,
            "profile_pic_url": self.profile_pic_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

        # Don't include sensitive info by default
        if include_sensitive:
            data.update({
                "address_lat": self.address_lat,
                "address_lon": self.address_lon,
                "auth_provider": self.auth_provider
            })

        return data
