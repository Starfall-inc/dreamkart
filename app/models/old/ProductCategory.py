from app.extensions import db


class ProductCategory(db.Model):
    __tablename__ = 'product_category'
    __table_args__ = {"schema": "none"}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    category_image = db.Column(db.String(255))
    description = db.Column(db.Text)  # Change String(255) → Text

    products = db.relationship('Product', backref='category_rel', lazy=True)

    def __repr__(self):
        return f'<ProductCategory {self.name}>'

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category_image": self.category_image,
            "description": self.description
        }
