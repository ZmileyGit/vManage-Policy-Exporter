from requests import Response
from abc import abstractmethod
from vmanage.auth import vManageSession
from vmanage.tool import JSONRequestHandler,APIListRequestHandler
from vmanage.dao import CollectionDAO,ModelDAO
from vmanage.policy.centralized.tool import DefinitionType
from vmanage.policy.centralized.model import PolicyFactory
from vmanage.policy.centralized.model import Definition,HubNSpokeDefinition
from vmanage.policy.centralized.model import MeshDefinition,ControlDefinition
from vmanage.policy.centralized.model import VPNMembershipDefinition,AppRouteDefinition
from vmanage.policy.centralized.model import DataDefinition,CflowdDefinition

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

class HubNSpokeDefinitionDAO(ModelDAO):
    MODEL = HubNSpokeDefinition
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
    MODEL = MeshDefinition
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
    MODEL = ControlDefinition
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
    TYPE = VPNMembershipDefinition
    RESOURCE = "/dataservice/template/policy/definition/vpnmembershipgroup"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def get_by_id(self,mid:str):
        url = self.session.server.url(VPNMembershipDefinitionDAO.ID_RESOURCE).format(mid=mid)
        response = self.session.get(url,allow_redirects=False)
        return VPNMembershipRequestHandler().handle(response)

class VPNMembershipRequestHandler(DefinitionRequestHandler):
    def handle_document(self,response:Response,document:dict):
        return VPNMembershipDefinition.from_dict(document)

class AppRouteDefinitionDAO(ModelDAO):
    MODEL = AppRouteDefinition
    RESOURCE = "/dataservice/template/policy/definition/approute"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def get_by_id(self,mid:str):
        url = self.session.server.url(AppRouteDefinitionDAO.ID_RESOURCE).format(mid=mid)
        response = self.session.get(url,allow_redirects=False)
        return AppRouteRequestHandler().handle(response)

class AppRouteRequestHandler(DefinitionRequestHandler):
    def handle_document(self,response:Response,document:dict):
        return AppRouteDefinition.from_dict(document)

class DataDefinitionDAO(ModelDAO):
    MODEL = DataDefinition
    RESOURCE = "/dataservice/template/policy/definition/data"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def get_by_id(self,mid:str):
        url = self.session.server.url(DataDefinitionDAO.ID_RESOURCE).format(mid=mid)
        response = self.session.get(url,allow_redirects=False)
        return DataDefinitionRequestHandler().handle(response)


class DataDefinitionRequestHandler(DefinitionRequestHandler):
    def handle_document(self,response:Response,document:dict):
        return DataDefinition.from_dict(document)

class CflowdDefinitionDAO(ModelDAO):
    TYPE = "cflowd"
    RESOURCE = "/dataservice/template/policy/definition/cflowd"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def get_by_id(self,mid:str):
        url = self.session.server.url(CflowdDefinitionDAO.ID_RESOURCE).format(mid=mid)
        response = self.session.get(url,allow_redirects=False)
        return CflowdDefinitionRequestHandler().handle(response)

class CflowdDefinitionRequestHandler(DefinitionRequestHandler):
    def handle_document(self,response:Response,document:dict):
        return CflowdDefinition.from_dict(document)