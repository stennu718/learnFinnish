"""SQLAlchemy models."""
from datetime import datetime

from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(100), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    srs_cards = relationship("SRSCard", back_populates="user", lazy="selectin")
    progress = relationship("UserProgress", back_populates="user", uselist=False, lazy="selectin")


class WordPair(Base):
    __tablename__ = "word_pairs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    estonian: Mapped[str] = mapped_column(String(255), index=True)
    finnish: Mapped[str] = mapped_column(String(255), index=True)
    estonian_example: Mapped[str] = mapped_column(Text, default="")
    finnish_example: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(100), default="general")
    difficulty: Mapped[int] = mapped_column(Integer, default=1)  # 1-5
    is_cognate: Mapped[bool] = mapped_column(Boolean, default=False)
    audio_url: Mapped[str] = mapped_column(String(500), default="")


class SRSCard(Base):
    __tablename__ = "srs_cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    word_pair_id: Mapped[int] = mapped_column(ForeignKey("word_pairs.id"))
    direction: Mapped[str] = mapped_column(String(20))  # "et_fi" or "fi_et"

    # SM-2 fields
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5)
    interval: Mapped[int] = mapped_column(Integer, default=0)  # days
    repetitions: Mapped[int] = mapped_column(Integer, default=0)
    next_review: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_reviewed: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="srs_cards")
    word_pair = relationship("WordPair", lazy="selectin")


class UserProgress(Base):
    __tablename__ = "user_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    total_reviews: Mapped[int] = mapped_column(Integer, default=0)
    correct_reviews: Mapped[int] = mapped_column(Integer, default=0)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=1)
    last_activity: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    user = relationship("User", back_populates="progress")
