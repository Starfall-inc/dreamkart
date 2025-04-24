# models/session.py
from app.models.base import Base, db
from datetime import datetime

class Session(Base):
    session_id = db.Column(db.String(255), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey(lambda: f"{Base.get_schema()}.user.id", ondelete='CASCADE'), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)

    # Relationship
    user = db.relationship('User', back_populates='sessions')

    def __repr__(self):
        return f'<Session {self.session_id}>'

    @property
    def is_expired(self):
        return datetime.utcnow() > self.expires_at