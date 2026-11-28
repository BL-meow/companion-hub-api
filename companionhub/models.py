from datetime import datetime, timezone
from .extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    role = db.Column(db.String(20), nullable=False, default="user", server_default="user")

    companions = db.relationship("Companion", back_populates="user")

class Companion(db.Model):
    __tablename__ = "companions"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    name = db.Column(db.String(100), nullable=False)
    personality = db.Column(db.Text, nullable=False)
    backstory = db.Column(db.Text, nullable=True)
    appearance = db.Column(db.Text, nullable=True)
    greeting = db.Column(db.Text, nullable=True)

    is_public = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    user = db.relationship("User", back_populates="companions")