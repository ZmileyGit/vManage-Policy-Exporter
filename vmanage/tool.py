from json.decoder import JSONDecodeError

from abc import ABC,abstractmethod
from requests import Response

from vmanage.error import UnhandledResponseError,CodedAPIError,APIError

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
        raise UnhandledResponseError("URL: {url}\nCode: {code}".format(url=response.url,code=response.status_code),response)
    def handle(self,response:Response,default=None):
        if self.handle_condition(response):
            return self.handle_response(response)
        elif self.next_handler:
            return self.next_handler.handle(response,default)
        elif default is not None:
            return default
        return self.unhandled_behavior(response)

class HTTPCodeRequestHandler(RequestHandler):
    def __init__(self,handled_code:int,**kwargs):
        super().__init__(**kwargs)
        self.code = handled_code
    def handle_condition(self,response:Response):
        return response.status_code == self.code
    def handle_response(self,response:Response):
        return True

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
    def handle_document(self,response:Response,document:dict):
        return document

class APIErrorRequestHandler(JSONRequestHandler):
    ERROR_FIELD = "error"
    def handle_document_condition(self,response:Response,document:dict):
        return APIErrorRequestHandler.ERROR_FIELD in document
    def handle_document(self,response:Response,document:dict):
        raw_error = document.get(APIErrorRequestHandler.ERROR_FIELD)
        error = APIError.from_dict(raw_error)
        raise CodedAPIError("URL: {url}\nCode: {code}".format(url=response.url,code=response.status_code),response,error)

class APIListRequestHandler(JSONRequestHandler):
    def handle_document_condition(self,response:Response,document:dict):
        condition = [
            response.status_code == 200,
            "data" in document
        ]
        return all(condition)