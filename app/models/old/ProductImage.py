from datetime import datetime
from app.extensions import db


class ProductImage(db.Model):
    __tablename__ = 'product_images'
    __table_args__ = {"schema": "none"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    # Define the relationship
    product = db.relationship("Product", back_populates="images")

    def __repr__(self):
        return f"<ProductImage {self.image_url}>"

    def to_dict(self):
        return {
            "id": self.id,
            "image_url": self.image_url
        }
