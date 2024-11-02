from jarvas import Jarvas

jarvas = Jarvas()
token_access = jarvas.create_token(email='testerUser@gmail.com',password='123')
jarvas.create_json_file(token_access)
jarvas.create_app(name="discord",description="This is the Discord API to answer the users", status="API")
