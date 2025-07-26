import unittest
from app import app
import json
from unittest.mock import patch, MagicMock

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_admin_dashboard_without_auth(self):
        """Test that admin dashboard redirects when not authenticated"""
        response = self.app.get('/admin-dashboard.html', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # Should be redirected to login page
        self.assertIn(b'Sign In', response.data)

    def test_admin_dashboard_with_non_admin_role(self):
        """Test that admin dashboard returns 403 for non-admin users"""
        with self.app.session_transaction() as session:
            # Set up a session with a non-admin role
            session['user_id'] = 'test_user_id'
            session['email'] = 'test@example.com'
            session['role'] = 'patient'

        response = self.app.get('/admin-dashboard.html')
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'Unauthorized Access', response.data)

    def test_admin_dashboard_with_admin_role(self):
        """Test that admin dashboard works with admin role"""
        with self.app.session_transaction() as session:
            # Set up a session with admin role
            session['user_id'] = 'admin_user_id'
            session['email'] = 'admin@example.com'
            session['role'] = 'admin'

        response = self.app.get('/admin-dashboard.html')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Admin Dashboard', response.data)

    def test_api_auth_check(self):
        """Test the auth check API endpoint"""
        # First with no auth
        response = self.app.get('/api/auth/check')
        data = json.loads(response.data)
        self.assertFalse(data['authenticated'])
        
        # Then with auth
        with self.app.session_transaction() as session:
            session['user_id'] = 'test_user_id'
            session['role'] = 'doctor'
            
        response = self.app.get('/api/auth/check')
        data = json.loads(response.data)
        self.assertTrue(data['authenticated'])
        self.assertEqual(data['role'], 'doctor')

    # New tests for authentication and authorization
    def test_login_success(self):
        """Test successful login flow"""
        test_data = {
            'uid': 'test_user_123',
            'email': 'test@example.com',
            'role': 'admin'
        }
        response = self.app.post('/api/auth/login', 
                                json=test_data,
                                content_type='application/json')
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # Verify session was set correctly
        with self.app.session_transaction() as session:
            self.assertEqual(session['user_id'], 'test_user_123')
            self.assertEqual(session['email'], 'test@example.com')
            self.assertEqual(session['role'], 'admin')

    def test_login_missing_fields(self):
        """Test login with missing required fields"""
        test_data = {
            'uid': 'test_user_123',
            # Missing email and role
        }
        response = self.app.post('/api/auth/login', 
                                json=test_data,
                                content_type='application/json')
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(response.status_code, 400)

    def test_logout(self):
        """Test logout functionality"""
        # First login
        with self.app.session_transaction() as session:
            session['user_id'] = 'test_user_id'
            session['email'] = 'test@example.com'
            session['role'] = 'admin'
        
        # Then logout
        response = self.app.post('/api/auth/logout')
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # Verify session was cleared
        with self.app.session_transaction() as session:
            self.assertNotIn('user_id', session)
            self.assertNotIn('email', session)
            self.assertNotIn('role', session)

    # Tests for admin dashboard features and CRUD operations
    @patch('app.genai.GenerativeModel')
    def test_get_drug_info_endpoint(self, mock_model):
        """Test the drug info API endpoint"""
        # Set up mock for AI response
        mock_response = MagicMock()
        mock_response.text = "## Therapeutic Uses\n- Test therapeutic use"
        mock_model.return_value.generate_content.return_value = mock_response
        
        # Setup authenticated admin session
        with self.app.session_transaction() as session:
            session['user_id'] = 'admin_user_id'
            session['email'] = 'admin@example.com'
            session['role'] = 'admin'
        
        test_data = {'drug_name': 'Aspirin'}
        response = self.app.post('/get_drug_info',
                                json=test_data,
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('response', data)
        self.assertIn('Therapeutic Uses', data['response'])

    @patch('app.genai.GenerativeModel')
    def test_get_drug_info_missing_name(self, mock_model):
        """Test drug info API with missing drug name"""
        # Setup authenticated admin session
        with self.app.session_transaction() as session:
            session['user_id'] = 'admin_user_id'
            session['role'] = 'admin'
        
        test_data = {}  # Empty data, no drug name
        response = self.app.post('/get_drug_info',
                                json=test_data,
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('No drug name provided', data['response'])

    @patch('app.genai.GenerativeModel')
    def test_symptom_checker_endpoint(self, mock_model):
        """Test the symptom checker API endpoint"""
        # Set up mock for AI response
        mock_response = MagicMock()
        mock_response.text = "## Recommended Over-the-Counter Treatments\n- Test treatment"
        mock_model.return_value.generate_content.return_value = mock_response
        
        # Setup authenticated session
        with self.app.session_transaction() as session:
            session['user_id'] = 'test_user_id'
            session['role'] = 'patient'
        
        test_data = {'symptoms': 'headache and fever'}
        response = self.app.post('/symptom_checker',
                                json=test_data,
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('response', data)
        self.assertIn('Recommended Over-the-Counter Treatments', data['response'])

    @patch('app.genai.GenerativeModel')
    def test_symptom_checker_missing_symptoms(self, mock_model):
        """Test symptom checker API with missing symptoms"""
        # Setup authenticated session
        with self.app.session_transaction() as session:
            session['user_id'] = 'test_user_id'
            session['role'] = 'patient'
        
        test_data = {}  # Empty data, no symptoms
        response = self.app.post('/symptom_checker',
                                json=test_data,
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('No symptoms provided', data['response'])

    # Test role-based access to dashboards
    def test_doctor_dashboard_access(self):
        """Test access control for doctor dashboard"""
        # Test without auth - should redirect
        response = self.app.get('/doctor-dashboard.html', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign In', response.data)
        
        # Test with wrong role - should redirect
        with self.app.session_transaction() as session:
            session['user_id'] = 'test_user_id'
            session['email'] = 'test@example.com'
            session['role'] = 'patient'
        
        response = self.app.get('/doctor-dashboard.html', follow_redirects=True)
        # Should redirect to standard dashboard
        self.assertEqual(response.status_code, 200)
        
        # Test with correct role
        with self.app.session_transaction() as session:
            session['user_id'] = 'doctor_id'
            session['email'] = 'doctor@example.com'
            session['role'] = 'doctor'
        
        response = self.app.get('/doctor-dashboard.html')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'doctor-dashboard', response.data.lower())

    def test_pharmacist_dashboard_access(self):
        """Test access control for pharmacist dashboard"""
        # Test with wrong role - should redirect
        with self.app.session_transaction() as session:
            session['user_id'] = 'test_user_id'
            session['role'] = 'patient'
        
        response = self.app.get('/pharmacist-dashboard.html', follow_redirects=True)
        # Should redirect to standard dashboard
        self.assertEqual(response.status_code, 200)
        
        # Test with correct role
        with self.app.session_transaction() as session:
            session['user_id'] = 'pharm_id'
            session['email'] = 'pharmacist@example.com'
            session['role'] = 'pharmacist'
        
        response = self.app.get('/pharmacist-dashboard.html')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'pharmacist-dashboard', response.data.lower())

    # Test error handling
    def test_page_not_found(self):
        """Test 404 error handling"""
        response = self.app.get('/nonexistent-page.html')
        self.assertEqual(response.status_code, 404)

    # Test admin features with simulated database operations
    @patch('app.flask_cors.CORS')
    @patch('app.genai.GenerativeModel')
    def test_api_error_handling(self, mock_model, mock_cors):
        """Test API error handling when AI service fails"""
        # Set up mock for AI service to raise an exception
        mock_model.return_value.generate_content.side_effect = Exception("AI Service Error")
        
        # Setup authenticated session
        with self.app.session_transaction() as session:
            session['user_id'] = 'admin_user_id'
            session['role'] = 'admin'
        
        # Test drug info API error handling
        test_data = {'drug_name': 'Aspirin'}
        response = self.app.post('/get_drug_info',
                                json=test_data,
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('Error', data['response'])
        
        # Test symptom checker API error handling
        test_data = {'symptoms': 'fever and headache'}
        response = self.app.post('/symptom_checker',
                                json=test_data,
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('Error', data['response'])

    # Test image processing API
    @patch('app.genai.GenerativeModel')
    def test_process_upload_image(self, mock_model):
        """Test the image processing endpoint"""
        # Set up mock for AI response
        mock_response = MagicMock()
        mock_response.text = "## Drug Information\n- **Drug Name**: Test Drug"
        mock_model.return_value.generate_content.return_value = mock_response
        
        # Setup authenticated session
        with self.app.session_transaction() as session:
            session['user_id'] = 'test_user_id'
            session['role'] = 'pharmacist'
        
        # Create a simple base64 image
        test_image_data = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD//gA+Q1JFQVRPUjogZ2QtanBlZyB2MS4wICh1c2luZyBJSkcgSlBFRyB2ODApLCBkZWZhdWx0IHF1YWxpdHkK/9sAQwAIBgYHBgUIBwcHCQkICgwUDQwLCwwZEhMPFB0aHx4dGhwcICQuJyAiLCMcHCg3KSwwMTQ0NB8nOT04MjwuMzQy/9sAQwEJCQkMCwwYDQ0YMiEcITIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIy"
        
        response = self.app.post('/process-upload', 
                               data={'image_data': test_image_data},
                               content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('result', data)
        self.assertIn('Drug Information', data['result'])

    def test_process_upload_no_image(self):
        """Test image processing with no image data"""
        # Setup authenticated session
        with self.app.session_transaction() as session:
            session['user_id'] = 'test_user_id'
            session['role'] = 'pharmacist'
        
        response = self.app.post('/process-upload', 
                               data={},  # No image data
                               content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('No image received', data['result'])

if __name__ == '__main__':
    unittest.main()
