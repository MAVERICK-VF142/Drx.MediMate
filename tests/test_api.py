import sys
import os
import pytest
from flask import Flask
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.routes.api_routes import api_bp

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_get_drug_info_missing(client):
    response = client.post('/api/get_drug_info', json={})
    assert response.status_code == 400
    assert 'No drug name provided' in response.get_json()['response']

def test_symptom_checker_missing(client):
    response = client.post('/api/symptom_checker', json={})
    assert response.status_code == 400
    assert 'No symptoms provided' in response.get_json()['response']

def test_check_drug_interactions_invalid(client):
    response = client.post('/api/check_drug_interactions', json={'drugs': []})
    assert response.status_code == 400
    assert 'At least two drugs must be selected' in response.get_json()['response']
