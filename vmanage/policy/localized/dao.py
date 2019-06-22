from requests import Response

from vmanage.auth import vManageSession
from vmanage.dao import ModelDAO,CollectionDAO
from vmanage.tool import APIListRequestHandler,APIErrorRequestHandler

from vmanage.policy.dao import PolicyDAO,DefinitionDAO,PolicyRequestHandler
from vmanage.policy.tool import PolicyType,DefinitionType,factory_memoization

from vmanage.policy.localized.model import PolicyFactory
from vmanage.policy.localized.model import CLIPolicy,LocalizedGUIPolicy
from vmanage.policy.localized.model import QoSMapDefinition,RewriteRuleDefinition
from vmanage.policy.localized.model import ACLv4Definition,ACLv6Definition
from vmanage.policy.localized.model import vEdgeRouteDefinition

class PoliciesDAO(CollectionDAO):
    RESOURCE = "/dataservice/template/policy/vedge"
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

class LocalizedPolicyDAO(PolicyDAO):
    RESOURCE = "/dataservice/template/policy/vedge"
    ID_RESOURCE = RESOURCE + "/{mid}"
    DETAIL_RESOURCE = RESOURCE + "/definition/{mid}"
    def resource(self,mid:str=None):
        if mid:
            return LocalizedPolicyDAO.ID_RESOURCE.format(mid=mid)
        return LocalizedPolicyDAO.RESOURCE
    def get_by_id(self,mid:str):
        url = self.session.server.url(LocalizedPolicyDAO.DETAIL_RESOURCE.format(mid=mid))
        response = self.session.get(url)
        document = PolicyRequestHandler(next_handler=APIErrorRequestHandler()).handle(response)
        return self.instance(document)

class LocalizedCLIPolicyDAO(LocalizedPolicyDAO):
    MODEL = CLIPolicy
    def instance(self,document:dict):
        return CLIPolicy.from_dict(document)

class LocalizedGUIPolicyDAO(LocalizedPolicyDAO):
    MODEL = LocalizedGUIPolicy
    def instance(self,document:dict):
        return LocalizedGUIPolicy.from_dict(document)

class PolicyDAOFactory:
    def __init__(self,session:vManageSession):
        self.session = session
    @factory_memoization
    def from_type(self,policy_type:PolicyType):
        if policy_type == PolicyType.CLI:
            return LocalizedCLIPolicyDAO(self.session)
        elif policy_type == PolicyType.FEATURE:
            return LocalizedGUIPolicyDAO(self.session)
        raise ValueError("Unsupported Policy Type: {0}".format(policy_type))

class QoSMapDefinitionDAO(DefinitionDAO):
    MODEL = QoSMapDefinition
    RESOURCE = "/dataservice/template/policy/definition/qosmap"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def resource(self,mid:str=None):
        if mid:
            return QoSMapDefinitionDAO.ID_RESOURCE.format(mid=mid)
        return QoSMapDefinitionDAO.RESOURCE
    def instance(self,document:dict):
        return QoSMapDefinition.from_dict(document)

class RewriteRuleDefinitionDAO(DefinitionDAO):
    MODEL = RewriteRuleDefinition
    RESOURCE = "/dataservice/template/policy/definition/rewriterule"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def resource(self,mid:str=None):
        if mid:
            return RewriteRuleDefinitionDAO.ID_RESOURCE.format(mid=mid)
        return RewriteRuleDefinitionDAO.RESOURCE
    def instance(self,document:dict):
        return RewriteRuleDefinition.from_dict(document)

class ACLv4DefinitionDAO(DefinitionDAO):
    MODEL = ACLv4Definition
    RESOURCE = "/dataservice/template/policy/definition/acl"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def resource(self,mid:str=None):
        if mid:
            return ACLv4DefinitionDAO.ID_RESOURCE.format(mid=mid)
        return ACLv4DefinitionDAO.RESOURCE
    def instance(self,document:dict):
        return ACLv4Definition.from_dict(document)

class ACLv6DefinitionDAO(DefinitionDAO):
    MODEL = ACLv6Definition
    RESOURCE = "/dataservice/template/policy/definition/aclv6"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def resource(self,mid:str=None):
        if mid:
            return ACLv6DefinitionDAO.ID_RESOURCE.format(mid=mid)
        return ACLv6DefinitionDAO.RESOURCE
    def instance(self,document:dict):
        return ACLv6Definition.from_dict(document)

class vEdgeRouteDefinitionDAO(DefinitionDAO):
    MODEL = vEdgeRouteDefinition
    RESOURCE = "/dataservice/template/policy/definition/vedgeroute"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def resource(self,mid:str=None):
        if mid:
            return vEdgeRouteDefinitionDAO.ID_RESOURCE.format(mid=mid)
        return vEdgeRouteDefinitionDAO.RESOURCE
    def instance(self,document:dict):
        return vEdgeRouteDefinition.from_dict(document)

class DefinitionDAOFactory:
    def __init__(self,session:vManageSession):
        self.session = session
    @factory_memoization
    def from_type(self,def_type:DefinitionType):
        if def_type == DefinitionType.QOS_MAP:
            return QoSMapDefinitionDAO(self.session)
        elif def_type == DefinitionType.REWRITE_RULE:
            return RewriteRuleDefinitionDAO(self.session)
        elif def_type == DefinitionType.ACLv4:
            return ACLv4DefinitionDAO(self.session)
        elif def_type == DefinitionType.ACLv6:
            return ACLv6DefinitionDAO(self.session)
        elif def_type == DefinitionType.ROUTE_POLICY:
            return vEdgeRouteDefinitionDAO(self.session)
        raise ValueError("Unsupported Definition Type: {0}".format(def_type))
