from requests import Response

from vmanage.auth import vManageSession
from vmanage.dao import ModelDAO
from vmanage.error import CodedAPIError
from vmanage.tool import JSONRequestHandler,APIErrorRequestHandler
from vmanage.tool import HTTPCodeRequestHandler

from vmanage.policy.tool import ReferenceType,factory_memoization

from vmanage.lists.model import List,ApplicationList,ListType
from vmanage.lists.model import ColorList,DataPrefixList
from vmanage.lists.model import Policer,PrefixList,SiteList
from vmanage.lists.model import SLAClass,TLOCList,VPNList

class ListRequestHandler(JSONRequestHandler):
    def handle_document_condition(self,response:Response,document:dict):
        return List.ID_FIELD in document

class ListCreationRequestHandler(ListRequestHandler):
    def handle_document_condition(self,response:Response,document:dict):
        is_list = super().handle_document_condition(response,document)
        return is_list and response.status_code == 200

class ListDAOFactory:
    def __init__(self,session:vManageSession):
        self.session = session
    @factory_memoization
    def from_type(self,ref_type:ListType):
        if ref_type == ListType.APP:
            return ApplicationListDAO(self.session)
        elif ref_type == ListType.COLOR:
            return ColorListDAO(self.session)
        elif ref_type == ListType.DATA_PREFIX:
            return DataPrefixListDAO(self.session)
        elif ref_type == ListType.POLICER:
            return PolicerDAO(self.session)
        elif ref_type == ListType.PREFIX:
            return PrefixListDAO(self.session)
        elif ref_type == ListType.SITE:
            return SiteListDAO(self.session)
        elif ref_type == ListType.SLA:
            return SLAClassDAO(self.session)
        elif ref_type == ListType.TLOC:
            return TLOCListDAO(self.session)
        elif ref_type == ListType.VPN:
            return VPNListDAO(self.session)
        raise ValueError("Unsupported Reference Type {0}".format(ref_type))
    @factory_memoization
    def from_reference_type(self,ref_type:ReferenceType):
        if ref_type == ReferenceType.APP_LIST:
            return ApplicationListDAO(self.session)
        elif ref_type == ReferenceType.COLOR_LIST:
            return ColorListDAO(self.session)
        elif ref_type == ReferenceType.DATA_PREFIX_LIST:
            return DataPrefixListDAO(self.session)
        elif ref_type == ReferenceType.POLICER:
            return PolicerDAO(self.session)
        elif ref_type == ReferenceType.PREFIX_LIST:
            return PrefixListDAO(self.session)
        elif ref_type == ReferenceType.SITE_LIST:
            return SiteListDAO(self.session)
        elif ref_type == ReferenceType.SLA_CLASS:
            return SLAClassDAO(self.session)
        elif ref_type == ReferenceType.TLOC_LIST:
            return TLOCListDAO(self.session)
        elif ref_type == ReferenceType.VPN_LIST:
            return VPNListDAO(self.session)
        raise ValueError("Unsupported Reference Type {0}".format(ref_type))

class ListDAO(ModelDAO):
    MAX_FORCE_ATTEMPTS = 10
    DUPLICATE_LIST_NAME_CODE = "POLICY0001"
    def get_by_id(self,mid:str):
        url = self.session.server.url(self.resource(mid=mid))
        response = self.session.get(url)
        document = ListRequestHandler(next_handler=APIErrorRequestHandler()).handle(response)
        return self.instance(document)
    def create(self,model:List):
        url = self.session.server.url(self.resource())
        payload = model.to_dict()
        del payload[List.ID_FIELD]
        response = self.session.post(url,json=payload)
        document = ListCreationRequestHandler(next_handler=APIErrorRequestHandler()).handle(response)
        model.id = document[List.ID_FIELD]
        return model
    def force_create(self,model:List,max_attempts=MAX_FORCE_ATTEMPTS):
        original = model.to_dict()
        attempt = True
        count = 1
        while attempt and count <= max_attempts:
            try:
                model = self.create(model)
            except CodedAPIError as error:
                attempt = error.error.code == ListDAO.DUPLICATE_LIST_NAME_CODE
                if not attempt or count == max_attempts:
                    raise
                model.name = "-{attempt}-{name}".format(attempt=count,name=original[List.NAME_FIELD])
                count += 1
            else:
                attempt = False
        return model

class ApplicationListDAO(ListDAO):
    MODEL = ApplicationList
    RESOURCE = "/dataservice/template/policy/list/app"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def resource(self,mid:str=None):
        if mid:
            return ApplicationListDAO.ID_RESOURCE.format(mid=mid)
        return ApplicationListDAO.RESOURCE
    def instance(self,document:dict):
        return ApplicationList.from_dict(document)

class ColorListDAO(ListDAO):
    MODEL = ColorList
    RESOURCE = "/dataservice/template/policy/list/color"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def resource(self,mid:str=None):
        if mid:
            return ColorListDAO.ID_RESOURCE.format(mid=mid)
        return ColorListDAO.RESOURCE
    def instance(self,document:dict):
        return ColorList.from_dict(document)

class DataPrefixListDAO(ListDAO):
    MODEL = DataPrefixList
    RESOURCE = "/dataservice/template/policy/list/dataprefix"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def resource(self,mid:str=None):
        if mid:
            return DataPrefixListDAO.ID_RESOURCE.format(mid=mid)
        return DataPrefixListDAO.RESOURCE
    def instance(self,document:dict):
        return DataPrefixList.from_dict(document)

class PolicerDAO(ListDAO):
    MODEL = Policer
    RESOURCE = "/dataservice/template/policy/list/policer"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def resource(self,mid:str=None):
        if mid:
            return PolicerDAO.ID_RESOURCE.format(mid=mid)
        return PolicerDAO.RESOURCE
    def instance(self,document:dict):
        return Policer.from_dict(document)

class PrefixListDAO(ListDAO):
    MODEL = PrefixList
    RESOURCE = "/dataservice/template/policy/list/prefix"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def resource(self,mid:str=None):
        if mid:
            return PrefixListDAO.ID_RESOURCE.format(mid=mid)
        return PrefixListDAO.RESOURCE
    def instance(self,document:dict):
        return PrefixList.from_dict(document)

class SiteListDAO(ListDAO):
    MODEL = SiteList
    RESOURCE = "/dataservice/template/policy/list/site"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def resource(self,mid:str=None):
        if mid:
            return SiteListDAO.ID_RESOURCE.format(mid=mid)
        return SiteListDAO.RESOURCE
    def instance(self,document:dict):
        return SiteList.from_dict(document)

class SLAClassDAO(ListDAO):
    MODEL = SLAClass
    RESOURCE = "/dataservice/template/policy/list/sla"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def resource(self,mid:str=None):
        if mid:
            return SLAClassDAO.ID_RESOURCE.format(mid=mid)
        return SLAClassDAO.RESOURCE
    def instance(self,document:dict):
        return SLAClass.from_dict(document)

class TLOCListDAO(ListDAO):
    MODEL = TLOCList
    RESOURCE = "/dataservice/template/policy/list/tloc"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def resource(self,mid:str=None):
        if mid:
            return TLOCListDAO.ID_RESOURCE.format(mid=mid)
        return TLOCListDAO.RESOURCE
    def instance(self,document:dict):
        return TLOCList.from_dict(document)

class VPNListDAO(ListDAO):
    MODEL = VPNList
    RESOURCE = "/dataservice/template/policy/list/vpn"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def resource(self,mid:str=None):
        if mid:
            return VPNListDAO.ID_RESOURCE.format(mid=mid)
        return VPNListDAO.RESOURCE
    def instance(self,document:dict):
        return VPNList.from_dict(document)