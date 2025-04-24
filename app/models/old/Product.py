from app.extensions import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB, ARRAY


class Product(db.Model):
    __tablename__ = 'products'
    __table_args__ = {"schema": "none"}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('product_category.id'))
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    is_available = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    is_popular = db.Column(db.Boolean, default=False)
    tags = db.Column(ARRAY(db.String(50)), default=[])

    # ✅ JSONB field for dynamic attributes
    attributes = db.Column(JSONB, nullable=True, default={})

    # Relationships
    reviews = db.relationship('ProductReview', backref='product', lazy=True, cascade='all, delete-orphan')
    cart_items = db.relationship('Cart', backref='product', lazy=True)
    order_details = db.relationship('OrderDetail', backref='product', lazy=True)
    featured = db.relationship('FeaturedProduct', backref='product', lazy=True, uselist=False)
    # One-to-Many Relationship with ProductImage
    images = db.relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")

    @property
    def average_rating(self):
        if not self.reviews:
            return 0
        return round(sum(review.rating for review in self.reviews) / len(self.reviews), 2)  # Rounds to 2 decimal places

    def __repr__(self):
        return f'<Product {self.name}>'

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": float(self.price),  # Convert Decimal to float
            "images": [image.to_dict() for image in self.images],  # Convert ProductImage
            "description": self.description,
            "stock_quantity": self.stock_quantity,
            "category_id": self.category_id,
            "is_available": self.is_available,
            "attributes": self.attributes,  # Include attributes in API responses
            "reviews": [review.to_dict() for review in self.reviews],  # ✅ Include user info
            "avg_rating": self.average_rating,
        }
