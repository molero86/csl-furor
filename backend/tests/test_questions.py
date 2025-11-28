import os
from fastapi.testclient import TestClient

# Use a file-based sqlite DB for tests to avoid issues with in-memory across engines
os.environ.setdefault("DATABASE_URL", "sqlite:///./backend_test.db")

from backend import main
from backend.database import Base, engine, SessionLocal

# Ensure tables exist in the test DB
Base.metadata.create_all(bind=engine)

# Override dependency to use the SessionLocal created by backend.database

def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

main.app.dependency_overrides[main.get_db] = override_get_db
client = TestClient(main.app)


def test_crud_questions():
    # Create
    resp = client.post("/questions", json={"phase": 1, "order": 1, "text": "Q1", "type": "text"})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "id" in data
    qid = data["id"]

    # List
    resp = client.get("/questions")
    assert resp.status_code == 200
    lst = resp.json()
    assert isinstance(lst, list)
    assert any(x["id"] == qid for x in lst)

    # Get single
    resp = client.get(f"/questions/{qid}")
    assert resp.status_code == 200
    assert resp.json()["text"] == "Q1"

    # Update
    resp = client.put(f"/questions/{qid}", json={"phase": 2, "order": 5, "text": "Q1 updated", "type": "choice"})
    assert resp.status_code == 200
    assert resp.json()["phase"] == 2
    assert resp.json()["text"] == "Q1 updated"

    # Delete
    resp = client.delete(f"/questions/{qid}")
    assert resp.status_code == 200

    # Not found after delete
    resp = client.get(f"/questions/{qid}")
    assert resp.status_code == 404
