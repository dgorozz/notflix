from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from typing import Optional

from api.database import get_db
from api.core import SessionState
from api import schemas, models
import api.crud.session as crud_session


router = APIRouter(prefix="/sessions")


@router.get("", response_model=list[schemas.Session])
def get_sessions(
    state: Optional[SessionState] = Query(None, title="state", description="Filter by state: 'watching' or 'finished'"), 
    db: Session = Depends(get_db)
):
    return crud_session.get_sessions(db, state)


@router.get("/{session_id}", response_model=schemas.Session)
def get_session_id_by_id(session_id: int, db: Session = Depends(get_db)):
    return crud_session.get_session_by_id(db, session_id)


@router.post("/{session_id}/next", response_model=schemas.Session)
def next_episode(session_id: int, db: Session = Depends(get_db)):
    return crud_session.next_episode(db, session_id)


@router.post("/{session_id}/previous", response_model=schemas.Session)
def previous_episode(session_id: int, db: Session = Depends(get_db)):
    return crud_session.previous_episode(db, session_id)


@router.post("/{session_id}/goto", response_model=schemas.Session)
def goto_episode(session_id: int, data: schemas.SessionUpdate, db: Session = Depends(get_db)):
    return crud_session.goto_episode(db, session_id, data.season, data.episode)


@router.post("/{session_id}/restart", response_model=schemas.Session)
def restart_session(session_id: int, db: Session = Depends(get_db)):
    return crud_session.restart_show(db, session_id)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session_by_id(session_id: int, db: Session = Depends(get_db)):
    crud_session.delete_session_by_id(db, session_id)
    return


