from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

from api.core import SessionState


# ======== SHOWS ======== 
class ShowBase(BaseModel):
    name: str = Field(...)
    description: str = Field(...)
    gender: str = Field(...)
    episodes: List[int] = Field(...)

class ShowCreate(ShowBase):
    pass

class Show(ShowBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# ======== SESSIONS ========
class SessionBase(BaseModel):
    show_id: Optional[int]
    season: int = Field(1, ge=1)
    episode: int = Field(1, ge=1)
    state: SessionState = Field(SessionState.watching)
    start_date: Optional[datetime] = Field(None)
    end_date: Optional[datetime] = Field(None)

class SessionCreate(SessionBase):
    show_id: int = Field(...)
    start_date: datetime = Field(...)
    pass

class SessionUpdate(BaseModel):
    season: Optional[int] = None
    episode: Optional[int] = None
    state: Optional[SessionState] = None
    end_date: datetime = Field(None)

class Session(SessionBase):
    id: int
    show: Optional[Show] = None

    model_config = ConfigDict(from_attributes=True)