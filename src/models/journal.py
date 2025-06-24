from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class JournalEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: datetime = Field(default_factory=datetime.now)
    title: str
    content: str
    symbol: Optional[str] = None
    tags: List[str] = [] 