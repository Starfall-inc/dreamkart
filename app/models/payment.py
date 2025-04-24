# models/payment.py
from app.models.base import Base, db

class PaymentMethod(Base):
    method_name = db.Column(db.String(50), nullable=False)
    details = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<PaymentMethod {self.method_name}>'

    def to_dict(self):
        return {
            "id": self.id,
            "method_name": self.method_name,
            "details": self.details,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class PaymentTransaction(Base):
    order_id = db.Column(db.Integer, db.ForeignKey(lambda: f"{Base.get_schema()}.order.id", ondelete="CASCADE"), nullable=False)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    payment_status = db.Column(db.String(50), default="PENDING")  # PENDING, CHARGED, FAILED
    payment_method = db.Column(db.String(50))  # UPI, CARD, NET_BANKING, etc.
    amount = db.Column(db.Numeric(10, 2), nullable=False)

    # Relationship
    order = db.relationship("Order", back_populates="payment_transactions")

    __table_args__ = (
        db.UniqueConstraint('transaction_id', name='unique_transaction_id'),
        {'schema': Base.get_schema()}
    )

    def __repr__(self):
        return f"<PaymentTransaction {self.transaction_id} - {self.payment_status}>"

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "transaction_id": self.transaction_id,
            "payment_status": self.payment_status,
            "payment_method": self.payment_method,
            "amount": float(self.amount),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }