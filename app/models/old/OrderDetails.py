from app.extensions import db


class OrderDetail(db.Model):
    __tablename__ = 'order_details'
    __table_args__ = {"schema": "none"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Float)

    def __repr__(self):
        return f'<OrderDetail {self.id}>'

    def calculate_subtotal(self):
        self.subtotal = self.quantity * self.price
        return self.subtotal
