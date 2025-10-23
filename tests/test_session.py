from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from api import models, schemas
from api.core import SessionState
from tests.test_show import _add_show_to_db


def _add_session_to_db(db: Session, show_id: int, season: int = 1, episode: int = 1, state: SessionState = SessionState.watching):
    session = models.Session(show_id=show_id, season=season, episode=episode, state=state)
    db.add(session)
    db.commit()
    return session


def _add_dummy_shows_to_db(db: Session):
    show1_raw = {"name": "Breaking Bad", "description": "Walter White es un químico ...", "gender": "Acción", "episodes": [3, 4, 3]}
    show2_raw = {"name": "Peaky Blinders", "description": "Ambientada en Birmingham ...", "gender": "Mafia", "episodes": [8, 7]}   
    show1 = models.Show(**show1_raw)
    show2 = models.Show(**show2_raw)
    db.add_all([show1, show2])
    db.commit() 
    return [show1, show2]


def test_get_all_sessions(client: TestClient, db: Session):

    shows = _add_dummy_shows_to_db(db)
    sessions = [_add_session_to_db(db, show_id=show.id) for show in shows]

    response = client.get("/sessions")

    data = response.json()

    assert response.status_code == 200
    assert len(sessions) == len(shows)
    for i, session in enumerate(sessions):
        assert data[i]["id"] == session.id
        assert data[i]["show_id"] == session.show_id
        assert data[i]["show_id"] == shows[i].id


def test_get_sessions_filtered_by_state(client: TestClient, db: Session):

    show1, show2 = _add_dummy_shows_to_db(db)
    session1 = _add_session_to_db(db, show_id=show1.id)
    session2 = _add_session_to_db(db, show_id=show2.id, state=SessionState.finished)

    response = client.get("/sessions?state=watching")

    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["id"] == session1.id

    response = client.get("/sessions?state=finished")

    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["id"] == session2.id


def test_get_sessions_filtered_by_unknown_state_throws_error(client: TestClient, db: Session):

    show1, show2 = _add_dummy_shows_to_db(db)
    session1 = _add_session_to_db(db, show_id=show1.id)
    session2 = _add_session_to_db(db, show_id=show2.id, state=SessionState.finished)

    response = client.get("/sessions?state=unknown_state")

    assert response.status_code == 422 # Unprocessable entity


def test_get_session_by_id(client: TestClient, db: Session):

    show, *_ = _add_dummy_shows_to_db(db)
    session = _add_session_to_db(db, show_id=show.id)

    response = client.get(f"/sessions/{session.id}")

    data = response.json()

    assert response.status_code == 200
    assert data["id"] == session.id
    assert data["season"] == session.season
    assert data["episode"] == session.episode
    assert data["state"] == session.state


def test_get_not_existing_session_throws_error(client: TestClient, db: Session):

    response = client.get(f"/sessions/200")

    assert response.status_code == 404 # Not found


def test_next_episode(client: TestClient, db: Session):

    show, *_ = _add_dummy_shows_to_db(db)
    session = _add_session_to_db(db, show_id=show.id)

    assert session.episode == 1

    response = client.post(f"/sessions/{session.id}/next")

    data = response.json()

    assert response.status_code == 200
    assert data["id"] == session.id
    assert data["season"] == session.season
    assert data["episode"] == 2


def test_next_episode_on_last_episode_set_session_finished(client: TestClient, db: Session):

    show = _add_show_to_db(db, "Dummy show", "This is a dummy show", "dummy", [1])
    session = _add_session_to_db(db, show_id=show.id)

    assert session.season == 1
    assert session.episode == 1
    assert session.state == SessionState.watching

    response = client.post(f"/sessions/{session.id}/next")

    data = response.json()

    assert response.status_code == 200
    assert data["id"] == session.id
    assert data["season"] == 1
    assert data["episode"] == 1
    assert data["state"] == SessionState.finished


def test_next_episode_on_last_episode_of_season_one_navigate_to_first_episode_of_season_two(client: TestClient, db: Session):

    show = _add_show_to_db(db, "Dummy show", "This is a dummy show", "dummy", [2, 3])
    session = _add_session_to_db(db, show_id=show.id, season=1, episode=2)

    assert session.season == 1
    assert session.episode == 2

    response = client.post(f"/sessions/{session.id}/next")

    data = response.json()

    assert response.status_code == 200
    assert data["id"] == session.id
    assert data["season"] == 2
    assert data["episode"] == 1


def test_previous_episode(client: TestClient, db: Session):

    show, *_ = _add_dummy_shows_to_db(db)
    session = _add_session_to_db(db, show_id=show.id, episode=2)

    assert session.episode == 2

    response = client.post(f"/sessions/{session.id}/previous")

    data = response.json()

    assert response.status_code == 200
    assert data["id"] == session.id
    assert data["season"] == session.season
    assert data["episode"] == 1


def test_previous_episode_on_first_episode_of_season_two_navigate_to_last_episode_of_season_one(client: TestClient, db: Session):

    show = _add_show_to_db(db, "Dummy show", "This is a dummy show", "dummy", [2, 3])
    session = _add_session_to_db(db, show_id=show.id, season=2, episode=1)

    assert session.season == 2
    assert session.episode == 1

    response = client.post(f"/sessions/{session.id}/previous")

    data = response.json()

    assert response.status_code == 200
    assert data["id"] == session.id
    assert data["season"] == 1
    assert data["episode"] == 2


def test_previous_episode_on_first_episode_throws_error(client: TestClient, db: Session):

    show = _add_show_to_db(db, "Dummy show", "This is a dummy show", "dummy", [2, 3])
    session = _add_session_to_db(db, show_id=show.id)

    response = client.post(f"/sessions/{session.id}/previous")

    assert response.status_code == 400 # Bad request


def test_goto_episode(client: TestClient, db: Session):

    show, *_ = _add_dummy_shows_to_db(db)
    session = _add_session_to_db(db, show_id=show.id)

    assert session.season == 1
    assert session.episode == 1

    goto_season = 2
    goto_episode = 3
    response = client.post(f"/sessions/{session.id}/goto", json={"season": goto_season, "episode": goto_episode})

    data = response.json()

    assert response.status_code == 200
    assert data["id"] == session.id
    assert data["season"] == goto_season
    assert data["episode"] == goto_episode


def test_navigate_through_finished_session_throws_error(client: TestClient, db: Session):

    show, *_ = _add_dummy_shows_to_db(db)
    session = _add_session_to_db(db, show_id=show.id)

    session.state = SessionState.finished

    assert session.state == SessionState.finished

    response = client.post(f"/sessions/{session.id}/goto", json={"season": 2, "episode": 2})

    assert response.status_code == 400

    response = client.post(f"/sessions/{session.id}/next")

    assert response.status_code == 400

    response = client.post(f"/sessions/{session.id}/previous")

    assert response.status_code == 400


def test_goto_unexisting_episode_throws_error(client: TestClient, db: Session):

    show, *_ = _add_dummy_shows_to_db(db)
    session = _add_session_to_db(db, show_id=show.id)

    goto_season = 200
    goto_episode = 3
    response = client.post(f"/sessions/{session.id}/goto", json={"season": goto_season, "episode": goto_episode})

    assert response.status_code == 404

    goto_season = 1
    goto_episode = 500
    response = client.post(f"/sessions/{session.id}/goto", json={"season": goto_season, "episode": goto_episode})

    assert response.status_code == 404


def test_restart_session(client: TestClient, db: Session):

    show, *_ = _add_dummy_shows_to_db(db)
    session = _add_session_to_db(db, show_id=show.id, season=2, episode=3)

    assert session.season == 2
    assert session.episode == 3

    response = client.post(f"/sessions/{session.id}/restart")

    data = response.json()

    assert response.status_code == 200
    assert data["id"] == session.id
    assert data["season"] == 1
    assert data["episode"] == 1
    assert data["episode"] == 1


def test_delete_session(client: TestClient, db: Session):

    show, *_ = _add_dummy_shows_to_db(db)
    session = _add_session_to_db(db, show_id=show.id, season=2, episode=3)

    response = client.delete(f"/sessions/{session.id}")

    assert response.status_code == 204
    
    session = db.get(models.Session, session.id)

    assert session is None


def test_delete_unexisting_session_throws_error(client: TestClient, db: Session):

    response = client.delete(f"/sessions/4545")

    assert response.status_code == 404