import pytest
# NO LONGER NEEDED: import sys, os
# NO LONGER NEEDED: sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Use a relative import to access the backend folder
from . import create_app

# -----------------------------
# Setup test client
# -----------------------------
@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        yield client

# -----------------------------
# Test home/index page
# -----------------------------
def test_index(client):
    response = client.get("/")
    assert response.status_code in (200, 302)
    assert b"Welcome" in response.data or b"Drx" in response.data

# -----------------------------
# Test feedback API
# -----------------------------
def test_feedback_success(client):
    response = client.post("/feedback", json={
        "name": "Atharva",
        "email": "atharva@test.com",
        "message": "Great platform!"
    })
    assert response.status_code in (200, 201)
    data = response.get_json()
    assert data is not None
    assert "success" in data.get("status", "").lower()

def test_feedback_missing_fields(client):
    response = client.post("/feedback", json={"name": "Atharva"})
    assert response.status_code in (400, 422)
    data = response.get_json()
    assert data is not None
    assert "error" in data

# -----------------------------
# Test login API
# -----------------------------
def test_login_invalid(client):
    response = client.post("/login", json={"username": "wrong", "password": "wrong"})
    assert response.status_code in (401, 403)
    data = response.get_json()
    assert "error" in data

# -----------------------------
# Test unknown route
# -----------------------------
def test_404(client):
    response = client.get("/this-route-does-not-exist")
    assert response.status_code == 404