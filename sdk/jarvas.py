import requests, json
from  datetime import datetime, timedelta
import os

class Jarvas:
    def __init__(self, social_media='discord', log=1, app_name='', auto_send_message=True, discord_channel = 0):
        self.url = "http://127.0.0.1:8000"
        self.socia_media = social_media
        self.phone = ''
        self.access_token = ''
        self.log = log
        self.name = app_name
        self.auto_send_message = auto_send_message

        self.discord_channel = discord_channel

    def view_users(self):
        try:
            response = requests.get(f"{self.url}/users/")
            return response.json()
        except:
            return {'message': 'Could not establish connection' }

    def sign_up(self,username: str, email: str, password: str):
        response = requests.post(
            f'{self.url}/users/',
            json = {
                'username': username,
                'email': email,
                'password': password,
            },
            )
        if response.status_code == 201:
            return response.json()
        else:
            return {'message': response.text}
    #app functions
    def read_apps(self):
        response = requests.get(
            f'{self.url}/apps/'
        )
        return response.json()
    def use_app(self,name):
        apps = self.read_apps()
        for app in apps['apps']: 
            if app['name'] == name:
                self.name = name
        return {'message': f'You are using the {self.name} app'}
    def create_app(self, name: str, description: str, status: str):
        self.name = name
        if self.access_token == '':
            return {'message' : 'you need a token access'}
        response = requests.post(
            f'{self.url}/apps/',
            headers={'Authorization': f'Bearer {self.access_token}'},
            json={
                'name' : name,
                'description' : description,
                'status' : status
            }
        )
        return response.json()
    def update_app(self,new_name: str, new_description: str, new_status: str):
        response = requests.put(
            f'{self.url}/apps/{self.name}',
            headers={'Authorization': f'Bearer {self.access_token}'},
            json={
                "name": new_name,
                "description": new_description,
                "status": new_status
            },
        )
        app_response = response.json()
        return app_response

    def send_message_discord(self):
        response = requests.post(
            f'{self.url}/sendMessage/discord/',  # Corrigido o endpoint
            json={
                "name": self.name,
                "id_channel": self.discord_channel
            }
        )
        return response
    def send_message_whatsapp(self):
        response = requests.post(
            f'{self.url}/apps/send_message/',
            headers={'Authorization': f'Bearer {self.access_token}'},
            json={
                "name": self.name,
                "phone": self.phone
            }
        )
        return response
    def change_state_app(self, status, send_message=1):
        apps = self.read_apps()
        for app in apps['apps']: 
            if app['name'] == self.name:
                response = self.update_app(
                    new_name=self.name,
                    new_description=app['description'],
                    new_status=status
                )
                if self.auto_send_message == True and send_message == 1:
                    if self.socia_media == "discord":
                        response = self.send_message_discord()
                    if self.socia_media == "whatsapp":
                        response = self.send_message_whatsapp()
                
                if self.log == 1:
                    try:
                        print("jarvas log: "+ response['detail'])
                    except:
                        print("jarvas log: " + status)
                return response

        message = f'The aplication with name {self.name} does not exist'
        if self.log == 1:
            print("jarvas log: " + message)
        return {'message': message}



    #Token functions   
    def create_token(self,email: str, password: str):
            try:
                response = requests.post(
                    f"{self.url}/auth/token",
                    data={'username': email, 'password': password},
                )
                date_created = datetime.now()
                date_expired = date_created + timedelta(minutes=10080)
                self.access_token = response.json()['access_token']
                return {
                    'access_token': response.json()['access_token'],
                    'token_type': response.json()['token_type'],
                    'date_created': str(date_created),
                    'date_expired': str(date_expired)
                }
            except:
                {'message': 'Could not establish connection'}

    
    def refresh_token(self,token):
        try: 
            response = requests.post(
                    f'{self.url}/auth/refresh_token',
                    headers={'Authorization': f'Bearer {token}'},
            )
            date_created = datetime.now()
            date_expired = date_created + timedelta(minutes=10080)
            return {
                    'access_token': response.json()['access_token'],
                    'token_type': response.json()['token_type'],
                    'date_created': str(date_created),
                    'date_expired': str(date_expired)
                }
        except requests.RequestException as e:
            return {'message': f'Could not establish connection {e}' }
    
    def verify_file_credentials(self,file):
        return os.path.isfile(file)

    def is_valid_token(self,file_name):
        with open(file_name, 'r', encoding='utf-8') as file:
            data = json.load(file)
        data_expired_str = data.get('date_expired')
        date_expired = datetime.fromisoformat(data_expired_str)
        date_atual = datetime.now()
        return date_atual < date_expired
    
    def create_json_file(self,dict, file_name='credentials.json'):
        with open(file_name, 'w', encoding='utf-8') as file:
            json.dump(dict, file, ensure_ascii=False, indent=4)

    def token(self, file):
        if self.verify_file_credentials(file):
            if self.is_valid_token(file):
                with open(file, 'r', encoding='utf-8') as filex:
                    data = json.load(filex)
                new_credentials = self.refresh_token(data.get('access_token'))
                self.access_token = new_credentials['access_token']
                self.create_json_file(new_credentials,file)
                return {'message': 'token was regenerate '}
            else:
                return {'message' : 'Create a token using the create_token function! '}
        else:
            return {'message' : 'Create a token using the create_token function! '}
