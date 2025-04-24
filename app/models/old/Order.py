from app.extensions import db
from datetime import datetime


class Order(db.Model):
    __tablename__ = 'orders'
    __table_args__ = {"schema" : "none"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    payment_method = db.Column(db.String(50), nullable=True)  # Changed from ForeignKey to String
    order_place_date = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    expected_delivery_date = db.Column(db.TIMESTAMP)
    actual_delivery_date = db.Column(db.TIMESTAMP)
    is_completed = db.Column(db.Boolean, default=False)
    total = db.Column(db.Numeric(10, 2))
    shipping_address = db.Column(db.String(255))
    status = db.Column(db.String(20), default='pending')
    delivery_charges = db.Column(db.Numeric(10, 2), default=0.00)
    coordinate_lat = db.Column(db.Float)
    coordinate_lon = db.Column(db.Float)

    user = db.relationship('User', back_populates='orders')

    order_details = db.relationship('OrderDetail', backref='order', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Order {self.id}>'

    @property
    def total_amount(self):
        return sum(detail.subtotal for detail in self.order_details) + float(self.delivery_charges or 0)