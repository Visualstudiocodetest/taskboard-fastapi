import os

from dotenv import load_dotenv

load_dotenv()
os.environ["DATABASE_URL"] = os.environ["TEST_DATABASE_URL"]

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


@pytest.fixture()
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return TestClient(app)


def make_project(client, name="Home"):
    return client.post("/api/projects", json={"name": name}).json()


def test_project_crud(client):
    p = make_project(client)
    assert client.get(f"/api/projects/{p['id']}").json()["name"] == "Home"
    r = client.put(f"/api/projects/{p['id']}", json={"name": "Work", "description": "d"})
    assert r.json()["name"] == "Work"
    assert client.delete(f"/api/projects/{p['id']}").status_code == 204
    assert client.get(f"/api/projects/{p['id']}").status_code == 404


def test_project_validation_and_duplicates(client):
    assert client.post("/api/projects", json={"name": "   "}).status_code == 422
    assert client.post("/api/projects", json={}).status_code == 422
    make_project(client)
    assert client.post("/api/projects", json={"name": "Home"}).status_code == 409


def test_task_lifecycle_and_count(client):
    p = make_project(client)
    r = client.post(f"/api/projects/{p['id']}/tasks", json={"title": "Buy milk", "priority": 1})
    assert r.status_code == 201
    t = r.json()
    assert client.patch(f"/api/tasks/{t['id']}", json={"done": True}).json()["done"] is True
    assert client.get(f"/api/projects/{p['id']}/tasks?done=false").json() == []
    assert client.get(f"/api/projects/{p['id']}").json()["task_count"] == 1
    assert client.delete(f"/api/tasks/{t['id']}").status_code == 204


def test_task_validation(client):
    p = make_project(client)
    url = f"/api/projects/{p['id']}/tasks"
    assert client.post(url, json={"title": "x", "priority": 9}).status_code == 422
    assert client.post(url, json={"title": ""}).status_code == 422
    assert client.post("/api/projects/999/tasks", json={"title": "x"}).status_code == 404
    assert client.patch("/api/tasks/999", json={"done": True}).status_code == 404
    t = client.post(url, json={"title": "x"}).json()
    assert client.patch(f"/api/tasks/{t['id']}", json={"title": None}).status_code == 422


def test_deleting_project_removes_tasks(client):
    p = make_project(client)
    t = client.post(f"/api/projects/{p['id']}/tasks", json={"title": "x"}).json()
    client.delete(f"/api/projects/{p['id']}")
    assert client.patch(f"/api/tasks/{t['id']}", json={"done": True}).status_code == 404
