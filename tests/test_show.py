from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from api import models, schemas


def _add_show_to_db(db: Session, name: str, description: str, gender: str, episodes: list[int]):
    show = models.Show(name=name, description=description, gender=gender, episodes=episodes)
    db.add(show)
    db.commit()
    return show


def test_get_all_shows(client: TestClient, db: Session):

    show1 = {"name": "Breaking Bad", "description": "Walter White es un químico ...", "gender": "Acción", "episodes": [3, 4, 3]}
    show2 = {"name": "Peaky Blinders", "description": "Ambientada en Birmingham ...", "gender": "Mafia", "episodes": [8, 7]}
    _add_show_to_db(db, **show1)
    _add_show_to_db(db, **show2)

    response = client.get("/shows")

    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["name"] == "Breaking Bad"
    assert data[1]["name"] == "Peaky Blinders"


def test_get_show_by_id(client: TestClient, db: Session):

    show = _add_show_to_db(db, name="Breaking Bad", description="Walter White es un químico ...", gender="Acción", episodes=[3, 4, 3])

    response = client.get(f"/shows/{show.id}")

    data = response.json()

    assert response.status_code == 200
    assert data["id"] == show.id
    assert data["name"] == show.name


def test_start_show(client: TestClient, db: Session):

    show = _add_show_to_db(db, name="Breaking Bad", description="Walter White es un químico ...", gender="Acción", episodes=[3, 4, 3])

    response = client.post(f"/shows/{show.id}/start")

    assert response.status_code == 200

    session = db.get(models.Session, 1) # first session created -> id=1
    assert session and session.show_id == show.id