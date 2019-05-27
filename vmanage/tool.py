from json.decoder import JSONDecodeError

from abc import ABC,abstractmethod
from requests import Response

from vmanage.error import UnhandledResponseError

class RequestHandler(ABC):
    def __init__(self,next_handler=None):
        self.next_handler = next_handler
    @abstractmethod
    def handle_condition(self,response:Response):
        pass
    @abstractmethod
    def handle_response(self,response:Response):
        pass
    def unhandled_behavior(self,response:Response):
        raise UnhandledResponseError("URL: {url}\nCode: {code}".format(url=response.url,code=response.status_code))
    def handle(self,response:Response,default=None):
        if self.handle_condition(response):
            return self.handle_response(response)
        elif self.next_handler:
            return self.next_handler.handle(response,default)
        elif default is not None:
            return default
        return self.unhandled_behavior(response)

class JSONRequestHandler(RequestHandler):
    def handle_condition(self,response:Response):
        try:
            document = response.json()
            return self.handle_document_condition(response,document)
        except JSONDecodeError:
            pass
        return False
    @abstractmethod
    def handle_document_condition(self,response:Response,document:dict):
        pass
    def handle_response(self,response:Response):
        return self.handle_document(response,response.json())
    @abstractmethod
    def handle_document(self,response:Response,document:dict):
        pass