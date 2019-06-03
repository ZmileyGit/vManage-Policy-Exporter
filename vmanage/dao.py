from requests import Response
from abc import ABC,abstractmethod
from vmanage.auth import vManageSession

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