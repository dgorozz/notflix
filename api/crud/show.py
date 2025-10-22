from sqlalchemy.orm import Session
from fastapi import HTTPException

from api import models
from api import schemas


def get_all_shows(db: Session):
    return db.query(models.Show).all()


def get_show_by_id(db: Session, show_id: int):
    show = db.query(models.Show).filter(models.Show.id == show_id).first()
    if not show:
        raise HTTPException(status_code=404, detail=f"Show with id {show_id} not found")
    return show


def create_show(db: Session, show: schemas.ShowCreate):
    db_show = models.Show(**show.model_dump())
    db.add(db_show)
    db.commit()
    db.refresh(db_show)
    return db_show