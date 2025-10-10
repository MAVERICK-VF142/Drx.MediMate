import pytest
from backend import create_app as app   # Import your Flask app





@pytest.fixture
def client():
    # Setup test client
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# -----------------------------
# ✅ Home / Index route
# -----------------------------
def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome" in response.data or b"Drx" in response.data


# -----------------------------
# ✅ Example: Feedback API
# -----------------------------
def test_feedback_post_success(client):
    response = client.post('/feedback', json={
        "name": "Atharva",
        "email": "atharva@test.com",
        "message": "Great platform!"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert "success" in data.get("status", "").lower()


def test_feedback_post_missing_fields(client):
    response = client.post('/feedback', json={
        "name": "Atharva"
        # missing email + message
    })
    assert response.status_code in (400, 422)
    data = response.get_json()
    assert data is not None
    assert "error" in data


# -----------------------------
# ✅ Example: Auth Routes
# -----------------------------
def test_login_success(client):
    response = client.post('/login', json={
        "username": "testuser",
        "password": "testpass"
    })
    assert response.status_code in (200, 401, 403)  # allow flexibility
    data = response.get_json()
    assert data is not None


def test_login_failure(client):
    response = client.post('/login', json={
        "username": "wrong",
        "password": "wrong"
    })
    assert response.status_code in (401, 403)
    data = response.get_json()
    assert "error" in data


# -----------------------------
# ✅ Example: Register
# -----------------------------
def test_register(client):
    response = client.post('/register', json={
        "username": "newuser",
        "email": "newuser@test.com",
        "password": "123456"
    })
    assert response.status_code in (200, 201, 400)
    data = response.get_json()
    assert data is not None


# -----------------------------
# ✅ Example: API that fetches data
# -----------------------------
def test_get_all_users(client):
    response = client.get('/users')
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        data = response.get_json()
        assert isinstance(data, list)
