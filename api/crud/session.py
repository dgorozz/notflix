from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from typing import Optional

from api import models
from api import schemas
from api.core import SessionState



def raise_error_if_finished(session: models.Session):
    if session.state == SessionState.finished:
        raise HTTPException(status_code=400, detail=f"Session with id {session.id} is marked as 'finished'. To navigate through episodes please restart it.")



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

    existing_session_with_same_showid = db.query(models.Session).filter(models.Session.show_id == session.show_id).first()
    if existing_session_with_same_showid:
        raise HTTPException(status_code=409, detail=f"Show with id {session.show_id} already started in session {existing_session_with_same_showid.id}")

    db_session = models.Session(**session.model_dump())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def next_episode(db: Session, session_id: int):
    session = get_session_by_id(db, session_id)

    raise_error_if_finished(session)

    show = session.show
    total_seasons = len(show.episodes)
    season = session.season
    episode = session.episode
    episodes_in_season = show.episodes[season - 1]

    if episode < episodes_in_season:
        session.episode += 1
    else:
        if season < total_seasons:
            session.season += 1
            session.episode = 1
        else:
            session.state = SessionState.finished

    db.commit()
    db.refresh(session)
    return session


def previous_episode(db: Session, session_id: int):
    session = get_session_by_id(db, session_id)

    raise_error_if_finished(session)

    show = session.show

    if session.episode > 1:
        session.episode -= 1
    elif session.season > 1:
        session.season -= 1
        session.episode = show.episodes[session.season - 1]
    else:
        raise HTTPException(status_code=400, detail="Already at first episode of the show")

    db.commit()
    db.refresh(session)
    return session


def goto_episode(db: Session, session_id: int, season: int, episode: int):
    session = get_session_by_id(db, session_id)

    raise_error_if_finished(session)

    show = session.show

    if season < 1 or season > len(show.episodes):
        raise HTTPException(status_code=404, detail=f"Season {season} does not exists. Show '{show.name}' only has {len(show.episodes)} seasons")

    if episode < 1 or episode > show.episodes[season - 1]:
        raise HTTPException(status_code=404, detail=f"Episode {episode} of season {season} does not exists. Season {season} of '{show.name}' only have {show.episodes[season - 1]} episodes.")

    session.season = season
    session.episode = episode
    session.state = SessionState.watching

    db.commit()
    db.refresh(session)
    return session


def restart_show(db: Session, session_id: int):
    session = get_session_by_id(db, session_id)
    session.season = 1
    session.episode = 1
    session.state = models.SessionState.watching
    db.commit()
    db.refresh(session)
    return session