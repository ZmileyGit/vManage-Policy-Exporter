from requests import Response
from abc import ABC,abstractmethod
from vmanage.entity import Model
from vmanage.auth import vManageSession
from vmanage.tool import HTTPCodeRequestHandler,APIErrorRequestHandler

class DAO(ABC):
    def __init__(self,session:vManageSession):
        self.session = session

class CollectionDAO(DAO):
    @abstractmethod
    def get_all(self):
        pass

class ModelDAO(DAO):
    @abstractmethod
    def resource(self,mid:str=None):
        pass
    @abstractmethod
    def instance(self,document:dict):
        pass
    @abstractmethod
    def get_by_id(self,mid:str):
        pass
    @abstractmethod
    def create(self,model:Model):
        pass
    def delete(self,mid:str):
        url = self.session.server.url(self.resource(mid=mid))
        response = self.session.delete(url)
        return HTTPCodeRequestHandler(200,next_handler=APIErrorRequestHandler()).handle(response)