from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from api.database import SessionLocal
from api.models import Show

import json


db = SessionLocal()


if __name__ == "__main__":

    with open("./source.json", "r", encoding="utf-8") as f:
        shows = json.loads(f.read())
    
    # print(shows)

    shows_db = []
    
    for show in shows:
        
        show_db = Show(
            name=show["name"],
            description=show["description"],
            gender=show["gender"],
            episodes=[v for v in show["episodes"].values()]
        )

        shows_db.append(show_db)
    
    db.add_all(shows_db)
    db.commit()