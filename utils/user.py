import requests
import os
from dotenv import load_dotenv

load_dotenv()


def is_admin(user_id, token_authorization):
    x_api_key = os.getenv('BACKOFFICE_API_KEY')
    r = requests.get(f'https://spotifiuby-api-gateway.herokuapp.com/users-api/users/{user_id}',
                     headers={'x-api-key': x_api_key, 'Authorization': token_authorization})
    user = r.json()
    return user['user_type'] == 'admin'
