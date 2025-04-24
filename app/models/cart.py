# models/cart.py
from app.models.base import Base, db
from datetime import datetime


class ShoppingCart(Base):
    """Shopping cart header."""
    user_id = db.Column(db.Integer, db.ForeignKey(lambda: f"{Base.get_schema()}.user.id"))
    session_id = db.Column(db.String(255), nullable=True)  # For guest carts
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    user = db.relationship('User', back_populates='carts')
    items = db.relationship('CartItem', back_populates='cart', cascade='all, delete-orphan')

    @property
    def total(self):
        return sum(item.line_total for item in self.items)

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items)

    def __repr__(self):
        return f'<ShoppingCart {self.id}>'

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "total": self.total,
            "item_count": self.item_count,
            "items": [item.to_dict() for item in self.items]
        }


class CartItem(Base):
    """Cart item detail."""
    cart_id = db.Column(db.Integer, db.ForeignKey(lambda: f"{Base.get_schema()}.shoppingcart.id", ondelete='CASCADE'))
    product_id = db.Column(db.Integer, db.ForeignKey(lambda: f"{Base.get_schema()}.product.id"))
    quantity = db.Column(db.Integer, default=1)

    # Relationships
    cart = db.relationship('ShoppingCart', back_populates='items')
    product = db.relationship('Product')

    __table_args__ = (
        db.UniqueConstraint('cart_id', 'product_id', name='unique_cart_product'),
        {'schema': Base.get_schema()}
    )

    @property
    def line_total(self):
        if not self.product:
            return 0
        return float(self.product.price) * self.quantity

    def __repr__(self):
        return f'<CartItem {self.id}>'

    def to_dict(self):
        return {
            "id": self.id,
            "cart_id": self.cart_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "line_total": self.line_total,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "product": {
                "name": self.product.name,
                "price": float(self.product.price),
                "image": self.product.images[0].image_url if self.product.images and self.product.images else None
            } if self.product else None
        }
