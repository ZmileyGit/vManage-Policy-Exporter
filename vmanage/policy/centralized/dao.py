from json import JSONDecoder

from requests import Response

from vmanage.auth import vManageSession
from vmanage.tool import JSONRequestHandler,APIListRequestHandler,APIErrorRequestHandler
from vmanage.tool import HTTPCodeRequestHandler
from vmanage.dao import CollectionDAO

from vmanage.policy.dao import PolicyDAO,DefinitionDAO,PolicyRequestHandler
from vmanage.policy.tool import factory_memoization,PolicyType
from vmanage.policy.model import CLIPolicy

from vmanage.policy.centralized.tool import DefinitionType
from vmanage.policy.centralized.model import PolicyFactory,Policy,CentralizedGUIPolicy
from vmanage.policy.centralized.model import Definition,HubNSpokeDefinition
from vmanage.policy.centralized.model import MeshDefinition,ControlDefinition
from vmanage.policy.centralized.model import VPNMembershipDefinition,AppRouteDefinition
from vmanage.policy.centralized.model import DataDefinition,CflowdDefinition

class CentralizedPolicyDAO(PolicyDAO):
    RESOURCE = "/dataservice/template/policy/vsmart"
    ID_RESOURCE = RESOURCE + "/{mid}"
    DETAIL_RESOURCE = RESOURCE + "/definition/{mid}"
    def resource(self,mid:str=None):
        if mid:
            return CentralizedPolicyDAO.ID_RESOURCE.format(mid=mid)
        return CentralizedPolicyDAO.RESOURCE
    def get_by_id(self,mid:str):
        url = self.session.server.url(CentralizedPolicyDAO.DETAIL_RESOURCE.format(mid=mid))
        response = self.session.get(url)
        document = PolicyRequestHandler(next_handler=APIErrorRequestHandler()).handle(response)
        return self.instance(document)

class CentralizedCLIPolicyDAO(CentralizedPolicyDAO):
    MODEL = CLIPolicy
    def instance(self,document:dict):
        return CLIPolicy.from_dict(document)

class CentralizedGUIPolicyDAO(CentralizedPolicyDAO):
    MODEL = CentralizedGUIPolicy
    def instance(self,document:dict):
        return CentralizedGUIPolicy.from_dict(document)
    def create(self,policy:Policy):
        url = self.session.server.url(self.resource())
        payload = policy.to_dict()
        payload[Policy.DEFINITION_FIELD] = JSONDecoder().decode(payload[Policy.DEFINITION_FIELD])
        del payload[Policy.ID_FIELD]
        response = self.session.post(url,json=payload)
        HTTPCodeRequestHandler(200,next_handler=APIErrorRequestHandler()).handle(response)
        policy.id = None
        return policy

class PolicyDAOFactory:
    def __init__(self,session:vManageSession):
        self.session = session
    @factory_memoization
    def from_type(self,policy_type:PolicyType):
        if policy_type == PolicyType.CLI:
            return CentralizedCLIPolicyDAO(self.session)
        elif policy_type == PolicyType.FEATURE:
            return CentralizedGUIPolicyDAO(self.session)
        raise ValueError("Unsupported Policy Type: {0}".format(policy_type))

class PoliciesDAO(CollectionDAO):
    RESOURCE = "/dataservice/template/policy/vsmart"
    def get_all(self):
        url = self.session.server.url(PoliciesDAO.RESOURCE)
        response = self.session.get(url)
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
