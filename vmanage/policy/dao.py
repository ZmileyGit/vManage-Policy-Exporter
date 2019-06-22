from requests import Response
from abc import abstractmethod

from vmanage.error import CodedAPIError
from vmanage.dao import ModelDAO
from vmanage.tool import JSONRequestHandler,APIErrorRequestHandler
from vmanage.tool import HTTPCodeRequestHandler

from vmanage.policy.model import Definition, Policy

class DefinitionRequestHandler(JSONRequestHandler):
    def handle_document_condition(self,response:Response,document:dict):
        return Definition.ID_FIELD in document

class DefinitionCreationRequestHandler(DefinitionRequestHandler):
    def handle_document_condition(self,response:Response,document:dict):
        is_definition = super().handle_document_condition(response,document)
        return is_definition and response.status_code == 200

class DefinitionDAO(ModelDAO):
    MAX_FORCE_ATTEMPTS = 10
    DUPLICATE_DEFINITION_NAME_CODE = "POLICY0001"
    def get_by_id(self,mid:str):
        url = self.session.server.url(self.resource(mid=mid))
        response = self.session.get(url)
        document = DefinitionRequestHandler(next_handler=APIErrorRequestHandler()).handle(response)
        return self.instance(document)
    def create(self,model:Definition):
        url = self.session.server.url(self.resource())
        payload = model.to_dict()
        del payload[Definition.ID_FIELD]
        response = self.session.post(url,json=payload)
        document = DefinitionCreationRequestHandler(next_handler=APIErrorRequestHandler()).handle(response)
        model.id = document[Definition.ID_FIELD]
        return model
    def force_create(self,model:Definition,max_attempts=MAX_FORCE_ATTEMPTS):
        original = model.to_dict()
        attempt = True
        count = 1
        while attempt and count <= max_attempts:
            try:
                model = self.create(model)
            except CodedAPIError as error:
                attempt = error.error.code == DefinitionDAO.DUPLICATE_DEFINITION_NAME_CODE
                if not attempt or count == max_attempts:
                    raise
                model.name = "-{attempt}-{name}".format(attempt=count,name=original[Definition.NAME_FIELD])
                count += 1
            else:
                attempt = False
        return model

class PolicyDAO(ModelDAO):
    MAX_FORCE_ATTEMPTS = 10
    DUPLICATE_POLICY_NAME_CODE = "POLICY0001"
    @abstractmethod
    def resource(self,mid:str=None):
        pass
    @abstractmethod
    def get_by_id(self,mid:str):
        pass
    def create(self,policy:Policy):
        url = self.session.server.url(self.resource())
        payload = policy.to_dict()
        del payload[Policy.ID_FIELD]
        response = self.session.post(url,json=payload)
        policy.id = None
        HTTPCodeRequestHandler(200,next_handler=APIErrorRequestHandler()).handle(response)
        return policy
    def force_create(self,model:Policy,max_attempts=MAX_FORCE_ATTEMPTS):
        original = model.to_dict()
        attempt = True
        count = 1
        while attempt and count <= max_attempts:
            try:
                model = self.create(model)
            except CodedAPIError as error:
                attempt = error.error.code == PolicyDAO.DUPLICATE_POLICY_NAME_CODE
                if not attempt or count == max_attempts:
                    print(model.to_dict())
                    print(error.error.message)
                    print(error.error.details)
                    print(error.error.code)
                    attempt = False
                model.name = "-{attempt}-{name}".format(attempt=count,name=original[Policy.NAME_FIELD])
                count += 1
            else:
                attempt = False
        return model

class PolicyRequestHandler(JSONRequestHandler):
    def handle_document_condition(self,response:Response,document:dict):
        return Policy.ID_FIELD in document