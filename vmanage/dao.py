from requests import Response
from abc import ABC,abstractmethod
from vmanage.auth import vManageSession
from vmanage.tool import JSONRequestHandler

class DAO(ABC):
    def __init__(self,session:vManageSession):
        self.session = session

class CollectionDAO(DAO):
    @abstractmethod
    def get_all(self):
        pass

class ModelDAO(DAO):
    @abstractmethod
    def get_by_id(self,mid:str):
        pass

class APIListRequestHandler(JSONRequestHandler):
    def handle_document_condition(self,response:Response,document:dict):
        condition = [
            response.status_code == 200,
            "data" in document
        ]
        return all(condition)