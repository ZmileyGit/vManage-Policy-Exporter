from requests import Response

from vmanage.auth import vManageSession
from vmanage.dao import ModelDAO,CollectionDAO
from vmanage.tool import APIListRequestHandler,APIErrorRequestHandler

from vmanage.policy.dao import PolicyDAO,DefinitionDAO,PolicyRequestHandler
from vmanage.policy.tool import PolicyType,factory_memoization

from vmanage.policy.localized.model import PolicyFactory
from vmanage.policy.localized.model import CLIPolicy,LocalizedGUIPolicy

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
    MODEL = None
    RESOURCE = "/dataservice/template/policy/definition/qosmap"
    ID_RESOURCE = RESOURCE + "/{mid}"

class RewriteRuleDefinitionDAO(DefinitionDAO):
    MODEL = None

class ACLv4DefinitionDAO(DefinitionDAO):
    MODEL = None

class ACLv6DefinitionDAO(DefinitionDAO):
    MODEL = None

class vEdgeRouteDefinitionDAO(DefinitionDAO):
    MODEL = None