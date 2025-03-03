from datetime import datetime

from pydantic import BaseModel, PositiveInt
from sqlalchemy import Column, Float, String, Integer, TIMESTAMP
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class RawData(Base):
    __tablename__ = "raw_data"
    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Float, nullable=False)
    base = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    updated_at = Column(
        TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
