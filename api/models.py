from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Integer, String, Column, ForeignKey, DateTime, Enum, JSON

from api.core import SessionState


class DecBase(DeclarativeBase):
    pass


class Show(DecBase):
    __tablename__ = "shows"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    episodes = Column(JSON, nullable=False)

    sessions = relationship("Session", back_populates="show", cascade="all, delete")


class Session(DecBase):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    show_id = Column(Integer, ForeignKey("shows.id", ondelete="CASCADE"), nullable=False)
    season = Column(Integer, default=1)
    episode = Column(Integer, default=1)
    state = Column(Enum(SessionState), default=SessionState.watching, nullable=False)
    start_date = Column(DateTime)
    end_date = Column(DateTime)

    show = relationship("Show", back_populates="sessions")