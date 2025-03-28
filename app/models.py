from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from .base import Base


class RecognitionResult(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True, index=True)
    audio_path = Column(String)
    text = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
