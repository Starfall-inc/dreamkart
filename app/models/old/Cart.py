# from your models file
from datetime import datetime
from app.extensions import db
from sqlalchemy.dialects.postgresql import ARRAY # You still have ARRAY imported here, maybe for other models?


class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Unique row ID
    cart_id = db.Column(db.String(20), unique=False)  # Now it's NOT a primary key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # Note: ForeignKey needs schema if 'users' isn't always in search_path! We'll get to that.
    product_id = db.Column(db.Integer, db.ForeignKey('products.id')) # Note: ForeignKey needs schema if 'products' isn't always in search_path!
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'product_id', name='unique_cart_item'),  # Positional arguments first
        {'schema': None} # <-- Add the schema as a dictionary at the end of the tuple!
    )

    def __repr__(self):
        return f'<Cart {self.cart_id}>'