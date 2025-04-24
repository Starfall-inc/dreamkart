from app.extensions import db
from datetime import datetime


class FeaturedProduct(db.Model):
    __tablename__ = 'featured_product'
    __table_args__ = {"schema": "none"}

    id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), primary_key=True)
    from_date = db.Column('from', db.TIMESTAMP, nullable=False)
    to_date = db.Column('to', db.TIMESTAMP, nullable=False)

    def __repr__(self):
        return f'<FeaturedProduct {self.id}>'

    @property
    def is_active(self):
        now = datetime.utcnow()
        return self.from_date <= now <= self.to_date