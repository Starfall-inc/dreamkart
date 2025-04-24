# models/store_settings.py
from app.models.base import Base, db
import json


class StoreSettings(Base):
    """Model for storing tenant-specific store settings."""

    # Basic store information
    store_name = db.Column(db.String(100), nullable=False)
    store_email = db.Column(db.String(100), nullable=False)
    store_phone = db.Column(db.String(20), nullable=True)
    store_address = db.Column(db.Text, nullable=True)
    store_currency_symbol = db.Column(db.String(10), default='$')

    # Store branding
    store_logo = db.Column(db.String(255), nullable=True)
    store_favicon = db.Column(db.String(255), nullable=True)

    # Theme settings - stored as JSON
    _store_theme = db.Column('store_theme', db.Text, nullable=False, default='{}')

    @property
    def store_theme(self):
        """Get the theme settings as a dictionary."""
        return json.loads(self._store_theme)

    @store_theme.setter
    def store_theme(self, theme_dict):
        """Store the theme settings as JSON string."""
        self._store_theme = json.dumps(theme_dict)

    def __repr__(self):
        return f'<StoreSettings {self.store_name}>'

    def to_dict(self):
        """Convert store settings to dictionary."""
        return {
            "id": str(self.id),
            "store_name": self.store_name,
            "store_email": self.store_email,
            "store_phone": self.store_phone,
            "store_address": self.store_address,
            "store_currency_symbol": self.store_currency_symbol,
            "store_logo": self.store_logo,
            "store_favicon": self.store_favicon,
            "store_theme": self.store_theme,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def get_settings(cls):
        """Get the current tenant's store settings."""
        return cls.query.first()

    @classmethod
    def initialize_default_settings(cls, store_name, store_email):
        """Create default store settings for a new tenant."""
        default_theme = {
            "primary": "#FFC0CB",
            "secondary": "#FF69B4",
            "text": "#4A4A4A",
            "background": "#FFF0F5",
            "dark": "#8B0000"
        }

        settings = cls(
            store_name=store_name,
            store_email=store_email,
            store_currency_symbol="$"
        )
        settings.store_theme = default_theme

        db.session.add(settings)
        db.session.commit()

        return settings