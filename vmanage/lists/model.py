from vmanage.entity import Model
from vmanage.lists.tool import ListType

class List(Model):
    ID_FIELD = "listId"
    NAME_FIELD = "name"
    NAME_LIMIT = 32
    DESCRIPTION_FIELD = "description"
    ENTRIES_FIELD = "entries"
    TYPE_FIELD = "type"
    def __init__(self,mid:str,name:str,list_type:str,description:str,entries:list):
        super().__init__(mid)
        self.name = name
        self._type = list_type
        self.description = description
        self.entries = entries
    @property
    def type(self):
        return ListType(self._type)
    def to_dict(self):
        return {
            List.ID_FIELD : self.id,
            List.NAME_FIELD : self.name[:List.NAME_LIMIT],
            List.TYPE_FIELD : self.type.value,
            List.DESCRIPTION_FIELD : self.description,
            List.ENTRIES_FIELD : self.entries
        }
    def __str__(self):
        return "{mid}({list_type}) -> '{name}'".format(mid=self.id,list_type=self.type,name=self.name)
    @classmethod
    def from_dict(klass,document:dict):
        mid = document.get(List.ID_FIELD)
        name = document.get(List.NAME_FIELD)
        list_type = document.get(List.TYPE_FIELD)
        description = document.get(List.DESCRIPTION_FIELD)
        entries = document.get(List.ENTRIES_FIELD,[])
        fields = [mid,name,list_type,description]
        if all(fields):
            return klass(mid,name,list_type,description,entries)

class ApplicationList(List):
    TYPE = ListType.APP

class ColorList(List):
    TYPE = ListType.COLOR

class DataPrefixList(List):
    TYPE = ListType.DATA_PREFIX

class Policer(List):
    TYPE = ListType.POLICER
    
class PrefixList(List):
    TYPE = ListType.PREFIX
    
class SiteList(List):
    TYPE = ListType.SITE

class SLAClass(List):
    TYPE = ListType.SLA

class TLOCList(List):
    TYPE = ListType.TLOC

class VPNList(List):
    TYPE = ListType.VPN

class ASPath(List):
    TYPE = ListType.AS_PATH

class Community(List):
    TYPE = ListType.COMMUNITY

class ExtendedCommunity(List):
    TYPE = ListType.EXTENDED_COMMUNITY

class ForwardingClass(List):
    TYPE = ListType.FORWARDING_CLASS

class Mirror(List):
    TYPE = ListType.MIRROR

class ListFactory:
    def from_dict(self,document):
        doc_type = ListType(document.get(List.TYPE_FIELD))
        if doc_type == ListType.APP:
            return ApplicationList.from_dict(document)
        elif doc_type == ListType.COLOR:
            return ColorList.from_dict(document)
        elif doc_type == ListType.DATA_PREFIX:
            return DataPrefixList.from_dict(document)
        elif doc_type == ListType.POLICER:
            return Policer.from_dict(document)
        elif doc_type == ListType.PREFIX:
            return PrefixList.from_dict(document)
        elif doc_type == ListType.SITE:
            return SiteList.from_dict(document)
        elif doc_type == ListType.SLA:
            return SLAClass.from_dict(document)
        elif doc_type == ListType.TLOC:
            return TLOCList.from_dict(document)
        elif doc_type == ListType.VPN:
            return VPNList.from_dict(document)
        elif doc_type == ListType.AS_PATH:
            return ASPath.from_dict(document)
        elif doc_type == ListType.COMMUNITY:
            return Community.from_dict(document)
        elif doc_type == ListType.EXTENDED_COMMUNITY:
            return ExtendedCommunity.from_dict(document)
        elif doc_type == ListType.FORWARDING_CLASS:
            return ForwardingClass.from_dict(document)
        elif doc_type == ListType.MIRROR:
            return Mirror.from_dict(document)
        raise ValueError("Unsupported List Type: {0}".format(doc_type))