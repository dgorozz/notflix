from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from typing import Optional

from api import models
from api import schemas
from api.core import SessionState



def get_sessions(db: Session, state: Optional[SessionState] = None):
    query = db.query(models.Session)
    if state:
        query = query.filter(models.Session.state == state)
    return query.all()


def get_session_by_id(db: Session, session_id: int):
    session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail=f"Session with id {session_id} not found")
    return session


def delete_session_by_id(db: Session, session_id: int):
    session = get_session_by_id(db, session_id)
    db.delete(session)
    db.commit()
    return None


def create_session(db: Session, session: schemas.SessionCreate):
    db_session = models.Session(**session.model_dump())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def next_episode(db: Session, session_id: int):
    session = get_session_by_id(db, session_id)
    show = session.show
    total_seasons = len(show.episodes)
    current_season = session.current_season
    current_episode = session.current_episode
    episodes_in_current_season = show.episodes[current_season - 1]

    if current_episode < episodes_in_current_season:
        session.current_episode += 1
    else:
        if current_season < total_seasons:
            session.current_season += 1
            session.current_episode = 1
        else:
            session.state = SessionState.finished

    db.commit()
    db.refresh(session)
    return session


def previous_episode(db: Session, session_id: int):
    session = get_session_by_id(db, session_id)
    show = session.show

    if session.current_episode > 1:
        session.current_episode -= 1
    elif session.current_season > 1:
        session.current_season -= 1
        session.current_episode = show.episodes[session.current_season - 1]
    else:
        raise HTTPException(status_code=400, detail="Ya estás en el primer episodio de la primera temporada")

    if session.state == SessionState.finished:
        session.state = SessionState.watching

    db.commit()
    db.refresh(session)
    return session


def goto_episode(db: Session, session_id: int, season: int, episode: int):
    session = get_session_by_id(db, session_id)
    show = session.show

    if season < 1 or season > len(show.episodes):
        raise HTTPException(status_code=400, detail=f"Season {season} does not exists. Show '{show.name}' only has {len(show.episodes)} seasons")

    if episode < 1 or episode > show.episodes[season - 1]:
        raise HTTPException(status_code=400, detail=f"Episode {episode} of season {season} does not exists. Season {season} of '{show.name}' only have {show.episodes[season - 1]} episodes.")

    session.current_season = season
    session.current_episode = episode
    session.state = SessionState.watching

    db.commit()
    db.refresh(session)
    return session


def restart_show(db: Session, session_id: int):
    session = get_session_by_id(db, session_id)
    session.current_season = 1
    session.current_episode = 1
    session.state = models.SessionState.watching
    db.commit()
    db.refresh(session)
    return session