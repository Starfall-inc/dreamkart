# models/marketing.py
from app.models.base import Base, db
from datetime import datetime

class Banner(Base):
    image_url = db.Column(db.String(255), nullable=True)
    title = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    link = db.Column(db.String(255), nullable=True)
    active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)  # Added for sorting

    def __repr__(self):
        return f'<Banner {self.title}>'

    def to_dict(self):
        return {
            "id": self.id,
            "image_url": self.image_url,
            "title": self.title,
            "description": self.description,
            "link": self.link,
            "active": self.active,
            "display_order": self.display_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }