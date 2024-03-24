from . models import User
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework import status

class ContactTestCase(APITestCase):
    
    """
    Test suite for Contact
    """
    def setUp(self):
        self.client = APIClient()
        self.data = {
            "first_name": "Mutale",
            "last_name": "Mwango",
            "username": "Mike",
            "email": "mutalemwango04@gmail.com",
            "password": "M@gna2020"

        }
        self.url = "/registration/"
    http http://127.0.0.1:8000/registration/ first_name= "Mutale" last_name = "Mwango" username: "Mike" email: "mutalemwango04@gmail.com" password: "M@gna2020"



    def test_create_contact(self):
        '''
        test ContactViewSet create method
        '''
        data = self.data
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Assert that the user was created in the database
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, data['username'])
        # Add more assertions as needed

