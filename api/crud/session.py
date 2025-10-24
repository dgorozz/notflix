from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from typing import Optional
from datetime import datetime
import logging

from api import models
from api import schemas
from api.core import SessionState


logger = logging.getLogger("crud:session")


def raise_error_if_finished(session: models.Session):
    if session.state == SessionState.finished:
        logger.warning(f"Attempted to navigate through finished session (id={session.id})")
        raise HTTPException(status_code=400, detail=f"Session with id {session.id} is marked as 'finished'. To navigate through episodes please restart it.")



def get_sessions(db: Session, state: Optional[SessionState] = None):
    logger.debug(f"Fetching all session from database")
    query = db.query(models.Session)
    if state:
        logger.debug(f"Applying filter to fetch session: state={state}")
        query = query.filter(models.Session.state == state)
    sessions = query.all()
    logger.debug(f"Sessions fetched from database: {len(sessions)}")
    return sessions


def get_session_by_id(db: Session, session_id: int):
    logger.debug(f"Fetching session with id={session_id} from database")
    session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not session:
        logger.error(f"Unexisting session (id={session_id})")
        raise HTTPException(status_code=404, detail=f"Session with id {session_id} not found")
    logger.debug("Session fetched from database")
    return session


def delete_session_by_id(db: Session, session_id: int):
    session = get_session_by_id(db, session_id)
    db.delete(session)
    db.commit()
    logger.debug(f"Session with id={session_id} succesfully removed from database")
    return None


def create_session(db: Session, session: schemas.SessionCreate):

    logger.debug(f"Trying to create a session for show={session.show_id}")
    existing_session_with_same_showid = db.query(models.Session).filter(models.Session.show_id == session.show_id).first()
    if existing_session_with_same_showid:
        logger.warning(f"Trying to create a session for show={session.show_id} which is already in another session (id={existing_session_with_same_showid.id})")
        raise HTTPException(status_code=409, detail=f"Show with id {session.show_id} already started in session {existing_session_with_same_showid.id}")

    db_session = models.Session(**session.model_dump())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    logger.debug(f"Session succesfully loaded to database (id={db_session.id})")
    return db_session


def next_episode(db: Session, session_id: int):

    session = get_session_by_id(db, session_id)

    raise_error_if_finished(session)

    logger.debug(f"Advancing session={session.id} to the next episode")
    show = session.show
    total_seasons = len(show.episodes)
    season = session.season
    episode = session.episode
    episodes_in_season = show.episodes[season - 1]

    if episode < episodes_in_season:
        session.episode += 1
        logger.info(f"Session with id={session.id} advanced one episode")
    else:
        if season < total_seasons:
            session.season += 1
            session.episode = 1
            logger.info(f"Session with id={session.id} advanced to the next season")
        else:
            session.end_date = datetime.today()
            session.state = SessionState.finished
            logger.info(f"Session with id={session.id} marked as finished")

    db.commit()
    db.refresh(session)
    logger.debug("Session succesfully updated")
    return session


def previous_episode(db: Session, session_id: int):
    session = get_session_by_id(db, session_id)

    raise_error_if_finished(session)

    logger.debug(f"Moving back session={session.id} to the previous episode")
    show = session.show

    if session.episode > 1:
        session.episode -= 1
        logger.info(f"Session with id={session.id} moved back one episode")
    elif session.season > 1:
        session.season -= 1
        session.episode = show.episodes[session.season - 1]
        logger.info(f"Session with id={session.id} moved back to the previous season")
    else:
        logger.warning(f"Session with id={session.id} is already on the first episode of the show")
        raise HTTPException(status_code=400, detail="Already at first episode of the show")

    db.commit()
    db.refresh(session)
    logger.debug("Session succesfully updated")
    return session


def goto_episode(db: Session, session_id: int, season: int, episode: int):
    session = get_session_by_id(db, session_id)

    raise_error_if_finished(session)

    logger.debug(f"Moving session with id={session.id} to season {season} and episode {episode}")
    show = session.show

    if season < 1 or season > len(show.episodes):
        logger.error(f"Session with id={session.id} does not have season {season}")
        raise HTTPException(status_code=404, detail=f"Season {season} does not exists. Show '{show.name}' only has {len(show.episodes)} seasons")

    if episode < 1 or episode > show.episodes[season - 1]:
        logger.error(f"Session with id={session.id} does not have episode {episode} for season {season}")
        raise HTTPException(status_code=404, detail=f"Episode {episode} of season {season} does not exists. Season {season} of '{show.name}' only have {show.episodes[season - 1]} episodes.")

    session.season = season
    session.episode = episode
    session.state = SessionState.watching

    db.commit()
    db.refresh(session)
    logger.debug("Session succesfully updated")
    return session


def restart_show(db: Session, session_id: int):
    session = get_session_by_id(db, session_id)
    logger.debug(f"Restarting session with id={session.id}")
    session.season = 1
    session.episode = 1
    session.end_date = None
    session.state = models.SessionState.watching
    db.commit()
    db.refresh(session)
    logger.debug("Session succesfully updated")
    return session