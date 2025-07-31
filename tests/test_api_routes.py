import unittest
import json
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the path to import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from backend.utils.gemini_utils import get_drug_information, get_symptom_recommendation


class TestAPIRoutes(unittest.TestCase):
    """Test cases for API routes"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
    def test_get_drug_info_missing_drug_name(self):
        """Test drug info endpoint with missing drug name"""
        response = self.client.post('/get_drug_info', 
                                  json={},
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('No drug name provided', data['response'])
        
    @patch('backend.routes.api_routes.get_drug_information')
    def test_get_drug_info_success(self, mock_get_drug_info):
        """Test successful drug info retrieval"""
        mock_get_drug_info.return_value = "Mock drug information"
        
        response = self.client.post('/get_drug_info',
                                  json={'drug_name': 'aspirin'},
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['response'], "Mock drug information")
        mock_get_drug_info.assert_called_once_with('aspirin')
        
    def test_symptom_checker_missing_symptoms(self):
        """Test symptom checker endpoint with missing symptoms"""
        response = self.client.post('/symptom_checker',
                                  json={},
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('No symptoms provided', data['response'])
        
    @patch('backend.routes.api_routes.get_symptom_recommendation')
    def test_symptom_checker_success(self, mock_get_symptoms):
        """Test successful symptom checking"""
        mock_get_symptoms.return_value = "Mock symptom recommendations"
        
        response = self.client.post('/symptom_checker',
                                  json={'symptoms': 'headache, fever'},
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['response'], "Mock symptom recommendations")
        mock_get_symptoms.assert_called_once_with('headache, fever')
        
    def test_allergy_checker_missing_data(self):
        """Test allergy checker with missing data"""
        # Test missing allergies
        response = self.client.post('/allergy_checker',
                                  json={'medicines': 'aspirin'},
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('No allergies provided', data['response'])
        
        # Test missing medicines
        response = self.client.post('/allergy_checker',
                                  json={'allergies': 'penicillin'},
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('No Medicines provided', data['response'])


if __name__ == '__main__':
    unittest.main()
