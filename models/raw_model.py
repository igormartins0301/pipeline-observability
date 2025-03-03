from datetime import datetime

from pydantic import BaseModel, PositiveInt


class RawData(BaseModel):
    amount: float
    base: str
    currency: str
    Timestamp: datetime
