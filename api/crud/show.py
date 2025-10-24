from sqlalchemy.orm import Session
from fastapi import HTTPException

import logging

from api import models
from api import schemas


logger = logging.getLogger("crud:show")


def get_all_shows(db: Session):
    logger.debug(f"Fetching all shows from database")
    shows = db.query(models.Show).all()
    logger.debug(f"Shows fetched from databaset: {len(shows)}")
    return shows


def get_show_by_id(db: Session, show_id: int):
    logger.debug(f"Fetching show with id={show_id} from database")
    show = db.query(models.Show).filter(models.Show.id == show_id).first()
    if not show:
        logger.error(f"Show with id={show_id} not found")
        raise HTTPException(status_code=404, detail=f"Show with id {show_id} not found")
    logger.info(f"Show with id={show_id} fetched from database")
    return show


def create_show(db: Session, show: schemas.ShowCreate):
    logger.debug(f"Trying to create a show")
    db_show = models.Show(**show.model_dump())
    db.add(db_show)
    db.commit()
    db.refresh(db_show)
    logger.info(f"Show succesfully created (id={db_show.id}, name={db_show.name})")
    return db_show