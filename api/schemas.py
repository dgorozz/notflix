from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

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
    show_id: int
    current_season: int = Field(1, ge=1)
    current_episode: int = Field(1, ge=1)
    state: SessionState = Field(SessionState.watching)

class SessionCreate(BaseModel):
    pass

class SessionUpdate(BaseModel):
    season: Optional[int] = None
    episode: Optional[int] = None
    state: Optional[SessionState] = None

class Session(SessionBase):
    id: int
    show: Optional[Show] = None

    model_config = ConfigDict(from_attributes=True)