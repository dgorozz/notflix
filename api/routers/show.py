from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from datetime import datetime

from api.database import get_db
from api import models, schemas
import api.crud.show as crud_show
import api.crud.session as crud_session


router = APIRouter(prefix="/shows")


@router.get("", response_model=list[schemas.Show])
def get_shows(db: Session = Depends(get_db)):
    return crud_show.get_all_shows(db)


@router.get("/{show_id}", response_model=schemas.Show)
def get_show_by_id(show_id: int, db: Session = Depends(get_db)):
    return crud_show.get_show_by_id(db, show_id)


@router.post("/{show_id}/start", response_model=schemas.Session)
def start_show(show_id: int, db: Session = Depends(get_db)):
    return crud_session.create_session(db, schemas.SessionCreate(show_id=show_id, start_date=datetime.today()))
