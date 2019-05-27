import json
import os
import getpass

from vmanage.entity import Server

class Configuration:
    SERVER_FIELD = "server"
    CREDENTIALS_FIELD = "creds"
    USERNAME_FIELD = "username"
    USERNAME_PROMPT = "Username: "
    PASSWORD_FIELD = "password"
    PASSWORD_PROMPT = "Password: "
    HOST_PROMPT = "Host: "
    PORT_PROMPT = "Port({0}): ".format(Server.DEFAULT_PORT)
    INVALID_PORT_NUMBER_MESSAGE = "Please input a port number"
    def __init__(self,server,username,password):
        self._server = server
        self._username = username
        self._password = password
    @property
    def username(self):
        if not self._username:
            self._username = input(Configuration.USERNAME_PROMPT)
        return self._username
    @property
    def password(self):
        if not self._password:
            self._password = getpass.getpass(Configuration.PASSWORD_PROMPT)
        return self._password
    @property
    def server(self):
        if not self._server:
            host = input(Configuration.HOST_PROMPT).strip()
            port = input(Configuration.PORT_PROMPT).strip()
            self._server = Server.from_dict({
                Server.HOST_FIELD : host,
                Server.PORT_FIELD : port
            })
        return self._server
    @staticmethod
    def from_dict(document:dict):
        server = document.get(Configuration.SERVER_FIELD,{})
        credentials = document.get(Configuration.CREDENTIALS_FIELD,{})
        server = Server.from_dict(server)
        username = credentials.get(Configuration.USERNAME_FIELD)
        password = credentials.get(Configuration.PASSWORD_FIELD)
        return Configuration(server,username,password)
    @staticmethod
    def from_file(path:str,**kwargs):
        json_config = {}
        if os.path.exists(path):
            with open(path,**kwargs) as raw_config:
                json_config = json.load(raw_config)
        return Configuration.from_dict(json_config)