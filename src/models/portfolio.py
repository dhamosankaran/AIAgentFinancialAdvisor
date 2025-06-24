from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PortfolioHolding(BaseModel):
    symbol: str
    shares: float
    purchase_price: float
    purchase_date: datetime
    notes: Optional[str] = None

class Transaction(BaseModel):
    id: str
    date: datetime
    type: str  # "buy" or "sell"
    symbol: str
    shares: float
    price: float
    total: float
    notes: Optional[str] = None 