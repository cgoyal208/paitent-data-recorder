from datetime import datetime

from extensions import db


class SystemSetting(db.Model):
    __tablename__ = "system_settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(80), unique=True, nullable=False, index=True)
    value = db.Column(db.String(255), nullable=False, default="retain")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SystemSetting {self.key}={self.value}>"
