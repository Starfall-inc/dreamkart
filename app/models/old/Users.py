from datetime import datetime
from app.extensions import db


class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {"schema": "none"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    password = db.Column(db.String(255))
    joined_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    default_location = db.Column(db.String(255))
    role = db.Column(db.String(20), default='customer')
    status = db.Column(db.String(20), default='active')
    cart_id = db.Column(db.String(25))  # Removed incorrect ForeignKey
    auth_provider = db.Column(
        db.Enum('google', 'manual', name='auth_provider_enum'),
        server_default='manual'
    )
    profile_pic_url = db.Column(db.String(255), default='none')
    address_lat = db.Column(db.String(255))
    address_lon = db.Column(db.String(255))

    # Relationships
    orders = db.relationship('Order', back_populates='user')
    reviews = db.relationship('ProductReview', backref='user', lazy=True, cascade='all, delete-orphan')
    cart_items = db.relationship('Cart', backref='user', lazy=True)
    sessions = db.relationship('Session', backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.email}>'
