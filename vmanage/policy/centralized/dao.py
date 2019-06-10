from json import JSONDecoder

from requests import Response
from abc import abstractmethod

from vmanage.auth import vManageSession
from vmanage.tool import JSONRequestHandler,APIListRequestHandler,APIErrorRequestHandler
from vmanage.tool import HTTPCodeRequestHandler
from vmanage.dao import CollectionDAO,ModelDAO
from vmanage.error import CodedAPIError

from vmanage.policy.tool import factory_memoization

from vmanage.policy.centralized.tool import DefinitionType
from vmanage.policy.centralized.model import PolicyFactory,Policy,PolicyType
from vmanage.policy.centralized.model import CLIPolicy,GUIPolicy
from vmanage.policy.centralized.model import Definition,HubNSpokeDefinition
from vmanage.policy.centralized.model import MeshDefinition,ControlDefinition
from vmanage.policy.centralized.model import VPNMembershipDefinition,AppRouteDefinition
from vmanage.policy.centralized.model import DataDefinition,CflowdDefinition

class PolicyDAO(ModelDAO):
    MAX_FORCE_ATTEMPTS = 10
    DUPLICATE_POLICY_NAME_CODE = "POLICY0001"
    RESOURCE = "/dataservice/template/policy/vsmart"
    ID_RESOURCE = RESOURCE + "/{mid}"
    DETAIL_RESOURCE = RESOURCE + "/definition/{mid}"
    def resource(self,mid:str=None):
        if mid:
            return PolicyDAO.ID_RESOURCE.format(mid=mid)
        return PolicyDAO.RESOURCE
    def get_by_id(self,mid:str):
        url = self.session.server.url(PolicyDAO.DETAIL_RESOURCE.format(mid=mid))
        response = self.session.get(url)
        document = PolicyRequestHandler(next_handler=APIErrorRequestHandler()).handle(response)
        return self.instance(document)
    def create(self,policy:Policy):
        url = self.session.server.url(self.resource())
        payload = policy.to_dict()
        del payload[Policy.ID_FIELD]
        response = self.session.post(url,json=payload,allow_redirects=False)
        HTTPCodeRequestHandler(200,next_handler=APIErrorRequestHandler()).handle(response)
        policy.id = None
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
                    print(error.error.message)
                    print(error.error.details)
                    attempt = False
                model.name = "-{attempt}-{name}".format(attempt=count,name=original[Policy.NAME_FIELD])
                count += 1
            else:
                attempt = False
        return model

class CLIPolicyDAO(PolicyDAO):
    MODEL = CLIPolicy
    def instance(self,document:dict):
        return CLIPolicy.from_dict(document)

class GUIPolicyDAO(PolicyDAO):
    MODEL = GUIPolicy
    def instance(self,document:dict):
        return GUIPolicy.from_dict(document)
    def create(self,policy:Policy):
        url = self.session.server.url(self.resource())
        payload = policy.to_dict()
        payload[Policy.DEFINITION_FIELD] = JSONDecoder().decode(payload[Policy.DEFINITION_FIELD])
        del payload[Policy.ID_FIELD]
        response = self.session.post(url,json=payload,allow_redirects=False)
        HTTPCodeRequestHandler(200,next_handler=APIErrorRequestHandler()).handle(response)
        policy.id = None
        return policy
    

class PolicyDAOFactory:
    def __init__(self,session:vManageSession):
        self.session = session
    @factory_memoization
    def from_type(self,policy_type:PolicyType):
        if policy_type == PolicyType.CLI:
            return CLIPolicyDAO(self.session)
        elif policy_type == PolicyType.FEATURE:
            return GUIPolicyDAO(self.session)
        raise ValueError("Unsupported Policy Type: {0}".format(policy_type))

class PolicyRequestHandler(JSONRequestHandler):
    def handle_document_condition(self,response:Response,document:dict):
        return Policy.ID_FIELD in document

class PoliciesDAO(CollectionDAO):
    RESOURCE = "/dataservice/template/policy/vsmart"
    def get_all(self):
        url = self.session.server.url(PoliciesDAO.RESOURCE)
        response = self.session.get(url,allow_redirects=False)
        return PoliciesRequestHandler().handle(response)
        
class PoliciesRequestHandler(APIListRequestHandler):
    def handle_document(self,response:Response,document:dict):
        data = document["data"]
        factory = PolicyFactory()
        policies = [factory.from_dict(raw_policy) for raw_policy in data]
        return policies

class DefinitionDAOFactory:
    def __init__(self,session:vManageSession):
        self.session = session
    @factory_memoization
    def from_type(self,definition_type:DefinitionType):
        if definition_type == HubNSpokeDefinition.TYPE:
            return HubNSpokeDefinitionDAO(self.session)
        elif definition_type == MeshDefinition.TYPE:
            return MeshDefinitionDAO(self.session)
        elif definition_type == ControlDefinition.TYPE:
            return ControlDefinitionDAO(self.session)
        elif definition_type == VPNMembershipDefinition.TYPE:
            return VPNMembershipDefinitionDAO(self.session)
        elif definition_type == AppRouteDefinition.TYPE:
            return AppRouteDefinitionDAO(self.session)
        elif definition_type == DataDefinition.TYPE:
            return DataDefinitionDAO(self.session)
        elif definition_type == CflowdDefinition.TYPE:
            return CflowdDefinitionDAO(self.session)

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
        response = self.session.get(url,allow_redirects=False)
        document = DefinitionRequestHandler(next_handler=APIErrorRequestHandler()).handle(response)
        return self.instance(document)
    def create(self,model:Definition):
        url = self.session.server.url(self.resource())
        payload = model.to_dict()
        del payload[Definition.ID_FIELD]
        response = self.session.post(url,json=payload,allow_redirects=False)
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

class HubNSpokeDefinitionDAO(DefinitionDAO):
    MODEL = HubNSpokeDefinition
    RESOURCE = "/dataservice/template/policy/definition/hubandspoke"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def resource(self,mid:str=None):
        if mid:
            return HubNSpokeDefinitionDAO.ID_RESOURCE.format(mid=mid)
        return HubNSpokeDefinitionDAO.RESOURCE
    def instance(self,document:dict):
        return HubNSpokeDefinition.from_dict(document)

class MeshDefinitionDAO(DefinitionDAO):
    MODEL = MeshDefinition
    RESOURCE = "/dataservice/template/policy/definition/mesh"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def resource(self,mid:str=None):
        if mid:
            return MeshDefinitionDAO.ID_RESOURCE.format(mid=mid)
        return MeshDefinitionDAO.RESOURCE
    def instance(self,document:dict):
        return MeshDefinition.from_dict(document)

class ControlDefinitionDAO(DefinitionDAO):
    MODEL = ControlDefinition
    RESOURCE = "/dataservice/template/policy/definition/control"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def resource(self,mid:str=None):
        if mid:
            return ControlDefinitionDAO.ID_RESOURCE.format(mid=mid)
        return ControlDefinitionDAO.RESOURCE
    def instance(self,document:dict):
        return ControlDefinition.from_dict(document)

class VPNMembershipDefinitionDAO(DefinitionDAO):
    TYPE = VPNMembershipDefinition
    RESOURCE = "/dataservice/template/policy/definition/vpnmembershipgroup"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def resource(self,mid:str=None):
        if mid:
            return VPNMembershipDefinitionDAO.ID_RESOURCE.format(mid=mid)
        return VPNMembershipDefinitionDAO.RESOURCE
    def instance(self,document:dict):
        return VPNMembershipDefinition.from_dict(document)

class AppRouteDefinitionDAO(DefinitionDAO):
    MODEL = AppRouteDefinition
    RESOURCE = "/dataservice/template/policy/definition/approute"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def resource(self,mid:str=None):
        if mid:
            return AppRouteDefinitionDAO.ID_RESOURCE.format(mid=mid)
        return AppRouteDefinitionDAO.RESOURCE
    def instance(self,document:dict):
        return AppRouteDefinition.from_dict(document)

class DataDefinitionDAO(DefinitionDAO):
    MODEL = DataDefinition
    RESOURCE = "/dataservice/template/policy/definition/data"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def resource(self,mid:str=None):
        if mid:
            return DataDefinitionDAO.ID_RESOURCE.format(mid=mid)
        return DataDefinitionDAO.RESOURCE
    def instance(self,document:dict):
        return DataDefinition.from_dict(document)

class CflowdDefinitionDAO(DefinitionDAO):
    TYPE = "cflowd"
    RESOURCE = "/dataservice/template/policy/definition/cflowd"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def resource(self,mid:str=None):
        if mid:
            return CflowdDefinitionDAO.ID_RESOURCE.format(mid=mid)
        return CflowdDefinitionDAO.RESOURCE
    def instance(self,document:dict):
        return CflowdDefinition.from_dict(document)
