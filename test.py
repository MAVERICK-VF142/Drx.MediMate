import unittest
from app import app

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_admin_dashboard(self):
        response = self.app.get('/admin-dashboard.html')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Admin Dashboard', response.data)

if __name__ == '__main__':
    unittest.main()
