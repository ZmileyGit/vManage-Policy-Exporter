import re

from requests import Session,Response
from vmanage.entity import Server
from vmanage.tool import RequestHandler,HTTPCodeRequestHandler

class vManageSession(Session):
    LOGIN_RESOURCE = "/j_security_check"
    CSRF_TOKEN_RESOURCE = "/dataservice/client/token"
    CSRF_HEADER = "X-XSRF-TOKEN"
    LOGOUT_RESOURCE = "/logout"
    def __init__(self,server:Server):
        super().__init__()
        self.server = server
    def __exit__(self,*args):
        super().__exit__(*args)
        self.logout()
    def login(self,username,password):
        payload = {
            "j_username" : username,
            "j_password" : password
        }
        url = self.server.url(vManageSession.LOGIN_RESOURCE)
        response = self.post(url,data=payload,verify=self.server.secure,allow_redirects=False)
        self.login = SuccessfulLoginHandler().handle(response)
        self.login = self.login and self.update_token()
        return self.login
    def update_token(self):
        if self.login:
            url = self.server.url(vManageSession.CSRF_TOKEN_RESOURCE)
            response = self.get(url,verify=self.server.secure,allow_redirects=False)
            token = TokenHandler().handle(response)
            if token is not None and len(token):
                token = token.strip()
                self.headers[vManageSession.CSRF_HEADER] = token
            return token is not None
        return False
    def logout(self):
        url = self.server.url(vManageSession.LOGOUT_RESOURCE)
        response = self.get(url,verify=self.server.secure,allow_redirects=False)
        return LogoutHandler().handle(response)

class TokenHandler(HTTPCodeRequestHandler):
    def __init__(self):
        super().__init__(200)
    def handle_response(self, response):
        return response.text
    def unhandled_behavior(self,response):
        return "" if response.status_code == 404 else None

class SuccessfulLoginHandler(RequestHandler):
    def handle_condition(self,response:Response):
        condition = [
            response.status_code == 200,
            not response.text
        ]
        return all(condition)
    def handle_response(self,response:Response):
        return True
    def unhandled_behavior(self,response:Response):
        return False

class LogoutHandler(RequestHandler):
    def handle_condition(self,response:Response):
        regex = re.compile(r'\s+<div +name="Login" +class="loginContainer">')
        condition = [
            response.status_code == 302 and not response.text,
            response.status_code == 200 and re.search(regex,response.text)
        ]
        return any(condition)
    def handle_response(self,response:Response):
        return True
    def unhandled_behavior(self,response:Response):
        return False