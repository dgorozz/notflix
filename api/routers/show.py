from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from datetime import datetime
import logging

from api.database import get_db
from api import models, schemas
import api.crud.show as crud_show
import api.crud.session as crud_session


logger = logging.getLogger("routers:show")


router = APIRouter(prefix="/shows")


@router.get("", response_model=list[schemas.Show])
def get_shows(db: Session = Depends(get_db)):
    logger.info(f"Received request to get all shows from database")
    shows = crud_show.get_all_shows(db)
    logger.info(f"Returned {len(shows)} shows")
    return shows


@router.get("/{show_id}", response_model=schemas.Show)
def get_show_by_id(show_id: int, db: Session = Depends(get_db)):
    logger.info(f"Received request to get show with id={show_id}")
    show = crud_show.get_show_by_id(db, show_id)
    logger.info(f"Show with id={show.id} returned succesfully")
    return show


@router.post("/{show_id}/start", response_model=schemas.Session)
def start_show(show_id: int, db: Session = Depends(get_db)):
    logger.info(f"Received request to start show with id={show_id}")
    session = crud_session.create_session(db, schemas.SessionCreate(show_id=show_id, start_date=datetime.today()))
    logger.info(f"Show with id={show_id} succesfully started")
    return session

