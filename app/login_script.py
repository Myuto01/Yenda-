import requests

url = "https://yenda-user-api.onrender.com/user_login/"
data = {'username': 'Essa', 'password': 'M@gna2020'}
response = requests.post(url, data=data)

print(response.json())  # Should return {'message': 'Login successful'} if successful
