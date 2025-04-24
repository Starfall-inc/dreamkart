# models/product.py
from app.models.base import Base, db
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from datetime import datetime


class ProductCategory(Base):
    name = db.Column(db.String(255), unique=True, nullable=False)
    category_image = db.Column(db.String(255))
    description = db.Column(db.Text)

    # Relationship
    products = db.relationship('Product', back_populates='category', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category_image": self.category_image,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Product(Base):
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey(lambda: f"{ProductCategory.get_schema()}.productcategory.id"))
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Numeric(10, 2), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    is_popular = db.Column(db.Boolean, default=False)
    tags = db.Column(ARRAY(db.String(50)), default=[])
    attributes = db.Column(JSONB, nullable=True, default={})

    # Relationships
    category = db.relationship('ProductCategory', back_populates='products')
    reviews = db.relationship('ProductReview', back_populates='product', lazy=True, cascade='all, delete-orphan')
    images = db.relationship('ProductImage', back_populates='product', cascade='all, delete-orphan')

    @property
    def average_rating(self):
        if not self.reviews:
            return 0
        return round(sum(review.rating for review in self.reviews) / len(self.reviews), 2)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": float(self.price),
            "description": self.description,
            "stock_quantity": self.stock_quantity,
            "category": self.category.to_dict() if self.category else None,
            "is_available": self.is_available,
            "attributes": self.attributes,
            "images": [image.to_dict() for image in self.images],
            "avg_rating": self.average_rating,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class ProductImage(Base):
    product_id = db.Column(db.Integer, db.ForeignKey(lambda: f"{Product.get_schema()}.product.id"), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    order = db.Column(db.Integer, default=0)  # Added for controlling image order

    # Relationship
    product = db.relationship('Product', back_populates='images')

    def to_dict(self):
        return {
            "id": self.id,
            "image_url": self.image_url,
            "order": self.order,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class ProductReview(Base):
    user_id = db.Column(db.Integer, db.ForeignKey(lambda: f"{Base.get_schema()}.user.id", ondelete='CASCADE'),
                        nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey(lambda: f"{Base.get_schema()}.product.id", ondelete='CASCADE'),
                           nullable=False)
    rating = db.Column(db.Integer)
    review_text = db.Column(db.Text)

    # Relationships
    user = db.relationship('User', back_populates='reviews')
    product = db.relationship('Product', back_populates='reviews')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'product_id', name='unique_user_product_review'),
        db.CheckConstraint('rating BETWEEN 1 AND 5', name='valid_rating_range'),
        {'schema': Base.get_schema()}
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "rating": self.rating,
            "review_text": self.review_text,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "user": {
                "profile_pic_url": self.user.profile_pic_url,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name
            } if self.user else None
        }


class FeaturedProduct(Base):
    product_id = db.Column(db.Integer, db.ForeignKey(lambda: f"{Base.get_schema()}.product.id", ondelete='CASCADE'),
                           primary_key=True)
    from_date = db.Column(db.DateTime, nullable=False)
    to_date = db.Column(db.DateTime, nullable=False)

    # Relationship
    product = db.relationship('Product', backref=db.backref('featured', uselist=False))

    @property
    def is_active(self):
        now = datetime.utcnow()
        return self.from_date <= now <= self.to_date