from requests import Response

from vmanage.auth import vManageSession
from vmanage.dao import ModelDAO
from vmanage.tool import JSONRequestHandler

from vmanage.policy.tool import ReferenceType

from vmanage.lists.model import List,ApplicationList
from vmanage.lists.model import ColorList,DataPrefixList
from vmanage.lists.model import Policer,PrefixList,SiteList
from vmanage.lists.model import SLAClass,TLOCList,VPNList

class ListRequestHandler(JSONRequestHandler):
    def handle_document_condition(self,response:Response,document:dict):
        return List.ID_FIELD in document

class ListDAOFactory:
    def __init__(self,session:vManageSession):
        self.session = session
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

class ApplicationListDAO(ModelDAO):
    MODEL = ApplicationList
    RESOURCE = "/dataservice/template/policy/list/app"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def get_by_id(self,mid:str):
        url = self.session.server.url(ApplicationListDAO.ID_RESOURCE.format(mid=mid))
        response = self.session.get(url)
        return ApplicationListRequestHandler().handle(response)

class ApplicationListRequestHandler(ListRequestHandler):
    def handle_document(self,response:Response,document:dict):
        return ApplicationList.from_dict(document)

class ColorListDAO(ModelDAO):
    MODEL = ColorList
    RESOURCE = "/dataservice/template/policy/list/color"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def get_by_id(self,mid:str):
        url = self.session.server.url(ColorListDAO.ID_RESOURCE.format(mid=mid))
        response = self.session.get(url)
        return ColorListRequestHandler().handle(response)

class ColorListRequestHandler(ListRequestHandler):
    def handle_document(self,response:Response,document:dict):
        return ColorList.from_dict(document)

class DataPrefixListDAO(ModelDAO):
    MODEL = DataPrefixList
    RESOURCE = "/dataservice/template/policy/list/dataprefix"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def get_by_id(self,mid:str):
        url = self.session.server.url(DataPrefixListDAO.ID_RESOURCE.format(mid=mid))
        response = self.session.get(url)
        return DataPrefixListRequestHandler().handle(response)

class DataPrefixListRequestHandler(ListRequestHandler):
    def handle_document(self,response:Response,document:dict):
        return DataPrefixList.from_dict(document)

class PolicerDAO(ModelDAO):
    MODEL = Policer
    RESOURCE = "/dataservice/template/policy/list/policer"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def get_by_id(self,mid:str):
        url = self.session.server.url(PolicerDAO.ID_RESOURCE.format(mid=mid))
        response = self.session.get(url)
        return PolicerRequestHandler().handle(response)

class PolicerRequestHandler(ListRequestHandler):
    def handle_document(self,response:Response,document:dict):
        return Policer.from_dict(document)

class PrefixListDAO(ModelDAO):
    MODEL = PrefixList
    RESOURCE = "/dataservice/template/policy/list/prefix"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def get_by_id(self,mid:str):
        url = self.session.server.url(PrefixListDAO.ID_RESOURCE.format(mid=mid))
        response = self.session.get(url)
        return PrefixListRequestHandler().handle(response)

class PrefixListRequestHandler(ListRequestHandler):
    def handle_document(self,response:Response,document:dict):
        return PrefixList.from_dict(document)

class SiteListDAO(ModelDAO):
    MODEL = SiteList
    RESOURCE = "/dataservice/template/policy/list/site"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def get_by_id(self,mid:str):
        url = self.session.server.url(SiteListDAO.ID_RESOURCE.format(mid=mid))
        response = self.session.get(url)
        return SiteListRequestHandler().handle(response)

class SiteListRequestHandler(ListRequestHandler):
    def handle_document(self,response:Response,document:dict):
        return SiteList.from_dict(document)

class SLAClassDAO(ModelDAO):
    MODEL = SLAClass
    RESOURCE = "/dataservice/template/policy/list/sla"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def get_by_id(self,mid:str):
        url = self.session.server.url(SLAClassDAO.ID_RESOURCE.format(mid=mid))
        response = self.session.get(url)
        return SLAClassRequestHandler().handle(response)

class SLAClassRequestHandler(ListRequestHandler):
    def handle_document(self,response:Response,document:dict):
        return SLAClass.from_dict(document)

class TLOCListDAO(ModelDAO):
    MODEL = TLOCList
    RESOURCE = "/dataservice/template/policy/list/tloc"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def get_by_id(self,mid:str):
        url = self.session.server.url(TLOCListDAO.ID_RESOURCE.format(mid=mid))
        response = self.session.get(url)
        return TLOCListRequestHandler().handle(response)

class TLOCListRequestHandler(ListRequestHandler):
    def handle_document(self,response:Response,document:dict):
        return TLOCList.from_dict(document)

class VPNListDAO(ModelDAO):
    MODEL = VPNList
    RESOURCE = "/dataservice/template/policy/list/vpn"
    ID_RESOURCE = RESOURCE + "/{mid}"
    def get_by_id(self,mid:str):
        url = self.session.server.url(VPNListDAO.ID_RESOURCE.format(mid=mid))
        response = self.session.get(url)
        return VPNListRequestHandler().handle(response)

class VPNListRequestHandler(ListRequestHandler):
    def handle_document(self,response:Response,document:dict):
        return VPNList.from_dict(document)