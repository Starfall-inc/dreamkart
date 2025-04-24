# models/order.py
from app.models.base import Base, db
from datetime import datetime


class Order(Base):
    user_id = db.Column(db.Integer, db.ForeignKey(lambda: f"{Base.get_schema()}.user.id"))
    payment_method = db.Column(db.String(50), nullable=True)
    expected_delivery_date = db.Column(db.DateTime)
    actual_delivery_date = db.Column(db.DateTime)
    is_completed = db.Column(db.Boolean, default=False)
    total = db.Column(db.Numeric(10, 2))
    shipping_address = db.Column(db.String(255))
    status = db.Column(db.String(20), default='pending')
    delivery_charges = db.Column(db.Numeric(10, 2), default=0.00)
    coordinate_lat = db.Column(db.Float)
    coordinate_lon = db.Column(db.Float)

    # Relationships
    user = db.relationship('User', back_populates='orders')
    order_details = db.relationship('OrderDetail', back_populates='order', lazy=True, cascade='all, delete-orphan')
    payment_transactions = db.relationship('PaymentTransaction', back_populates='order', lazy=True)

    @property
    def total_amount(self):
        return sum(detail.subtotal for detail in self.order_details) + float(self.delivery_charges or 0)

    def __repr__(self):
        return f'<Order {self.id}>'

    def to_dict(self, include_details=False):
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "payment_method": self.payment_method,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expected_delivery_date": self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            "actual_delivery_date": self.actual_delivery_date.isoformat() if self.actual_delivery_date else None,
            "is_completed": self.is_completed,
            "total": float(self.total) if self.total else self.total_amount,
            "shipping_address": self.shipping_address,
            "status": self.status,
            "delivery_charges": float(self.delivery_charges) if self.delivery_charges else 0,
        }

        if include_details:
            data["order_details"] = [detail.to_dict() for detail in self.order_details]
            data["payment_transactions"] = [tx.to_dict() for tx in self.payment_transactions]

        return data


class OrderDetail(Base):
    order_id = db.Column(db.Integer, db.ForeignKey(lambda: f"{Base.get_schema()}.order.id", ondelete='CASCADE'))
    product_id = db.Column(db.Integer, db.ForeignKey(lambda: f"{Base.get_schema()}.product.id", ondelete='CASCADE'))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Float)

    # Relationships
    order = db.relationship('Order', back_populates='order_details')
    product = db.relationship('Product')

    def __repr__(self):
        return f'<OrderDetail {self.id}>'

    def calculate_subtotal(self):
        self.subtotal = float(self.price) * self.quantity
        return self.subtotal

    def to_dict(self):
        if not self.subtotal:
            self.calculate_subtotal()

        return {
            "id": self.id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "price": float(self.price),
            "subtotal": self.subtotal,
            "product": {
                "name": self.product.name,
                "image": self.product.images[0].image_url if self.product.images else None
            } if self.product else None
        }
