from requests import Response
from abc import abstractmethod
from vmanage.auth import vManageSession
from vmanage.tool import JSONRequestHandler
from vmanage.dao import CollectionDAO,ModelDAO,APIListRequestHandler
from vmanage.policy.centralized.model import PolicyFactory
from vmanage.policy.centralized.model import Definition,HubNSpokeDefinition
from vmanage.policy.centralized.model import MeshDefinition,ControlDefinition

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
    def from_type(self,definition_type:str):
        if definition_type == HubNSpokeDefinitionDAO.TYPE:
            return HubNSpokeDefinitionDAO(self.session)
        elif definition_type == MeshDefinitionDAO.TYPE:
            return MeshDefinitionDAO(self.session)
        elif definition_type == ControlDefinitionDAO.TYPE:
            return ControlDefinitionDAO(self.session)
        elif definition_type == VPNMembershipDefinitionDAO.TYPE:
            return VPNMembershipDefinitionDAO(self.session)
        elif definition_type == AppRouteDefinitionDAO.TYPE:
            return AppRouteDefinitionDAO(self.session)
        elif definition_type == DataDefinitionDAO.TYPE:
            return DataDefinitionDAO(self.session)
        elif definition_type == CflowdDefinitionDAO.TYPE:
            return CflowdDefinitionDAO(self.session)

class DefinitionRequestHandler(JSONRequestHandler):
    def handle_document_condition(self,response:Response,document:dict):
        return Definition.ID_FIELD in document

class HubNSpokeDefinitionDAO(ModelDAO):
    TYPE = "hubAndSpoke"
    RESOURCE = "/dataservice/template/policy/definition/hubandspoke"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def get_by_id(self,mid:str):
        url = self.session.server.url(HubNSpokeDefinitionDAO.ID_RESOURCE).format(mid=mid)
        response = self.session.get(url,allow_redirects=False)
        return HubNSpokeRequestHandler().handle(response)

class HubNSpokeRequestHandler(DefinitionRequestHandler):
    def handle_document(self,response:Response,document:dict):
        return HubNSpokeDefinition.from_dict(document)

class MeshDefinitionDAO(ModelDAO):
    TYPE = "mesh"
    RESOURCE = "/dataservice/template/policy/definition/mesh"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def get_by_id(self,mid:str):
        url = self.session.server.url(MeshDefinitionDAO.ID_RESOURCE).format(mid=mid)
        response = self.session.get(url,allow_redirects=False)
        return MeshRequestHandler().handle(response)

class MeshRequestHandler(DefinitionRequestHandler):
    def handle_document(self,response:Response,document:dict):
        return MeshDefinition.from_dict(document)

class ControlDefinitionDAO(ModelDAO):
    TYPE = "control"
    RESOURCE = "/dataservice/template/policy/definition/control"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def get_by_id(self,mid:str):
        url = self.session.server.url(ControlDefinitionDAO.ID_RESOURCE).format(mid=mid)
        response = self.session.get(url,allow_redirects=False)
        return ControlRequestHandler().handle(response)

class ControlRequestHandler(DefinitionRequestHandler):
    def handle_document(self,response:Response,document:dict):
        return ControlDefinition.from_dict(document)

class VPNMembershipDefinitionDAO(ModelDAO):
    TYPE = "vpnMembershipGroup"
    RESOURCE = "/dataservice/template/policy/definition/vpnmembershipgroup"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def get_by_id(self,mid:str):
        url = self.session.server.url(VPNMembershipDefinitionDAO.ID_RESOURCE).format(mid=mid)
        response = self.session.get(url,allow_redirects=False)

class AppRouteDefinitionDAO(ModelDAO):
    TYPE = "appRoute"
    RESOURCE = "/dataservice/template/policy/definition/approute"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def get_by_id(self,mid:str):
        url = self.session.server.url(AppRouteDefinitionDAO.ID_RESOURCE).format(mid=mid)
        response = self.session.get(url,allow_redirects=False)

class DataDefinitionDAO(ModelDAO):
    TYPE = "data"
    RESOURCE = "/dataservice/template/policy/definition/data"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def get_by_id(self,mid:str):
        url = self.session.server.url(DataDefinitionDAO.ID_RESOURCE).format(mid=mid)
        response = self.session.get(url,allow_redirects=False)

class CflowdDefinitionDAO(ModelDAO):
    TYPE = "cflowd"
    RESOURCE = "/dataservice/template/policy/definition/cflowd"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def get_by_id(self,mid:str):
        url = self.session.server.url(CflowdDefinitionDAO.ID_RESOURCE).format(mid=mid)
        response = self.session.get(url,allow_redirects=False)