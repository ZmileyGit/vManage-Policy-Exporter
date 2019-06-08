from vmanage.entity import Model
from vmanage.lists.tool import ListType

class List(Model):
    ID_FIELD = "listId"
    NAME_FIELD = "name"
    DESCRIPTION_FIELD = "description"
    ENTRIES_FIELD = "entries"
    TYPE_FIELD = "type"
    def __init__(self,mid:str,name:str,description:str,entries:list):
        super().__init__(mid)
        self.name = name
        self.description = description
        self.entries = entries
    def to_dict(self):
        return {
            List.ID_FIELD : self.id,
            List.NAME_FIELD : self.name,
            List.DESCRIPTION_FIELD : self.description,
            List.ENTRIES_FIELD : self.entries
        }
    @classmethod
    def from_dict(klass,document:dict):
        mid = document.get(List.ID_FIELD)
        name = document.get(List.NAME_FIELD)
        description = document.get(List.DESCRIPTION_FIELD)
        entries = document.get(List.ENTRIES_FIELD,[])
        fields = [mid,name,description]
        if all(fields):
            return klass(mid,name,description,entries)

class ApplicationList(List):
    TYPE = ListType.APP
    def to_dict(self):
        result = super().to_dict()
        result[List.TYPE_FIELD] = ApplicationList.TYPE.value
        return result

class ColorList(List):
    TYPE = ListType.COLOR
    def to_dict(self):
        result = super().to_dict()
        result[List.TYPE_FIELD] = ColorList.TYPE.value
        return result

class DataPrefixList(List):
    TYPE = ListType.DATA_PREFIX
    def to_dict(self):
        result = super().to_dict()
        result[List.TYPE_FIELD] = DataPrefixList.TYPE.value
        return result

class Policer(List):
    TYPE = ListType.POLICER
    def to_dict(self):
        result = super().to_dict()
        result[List.TYPE_FIELD] = Policer.TYPE.value
        return result
    
class PrefixList(List):
    TYPE = ListType.PREFIX
    def to_dict(self):
        result = super().to_dict()
        result[List.TYPE_FIELD] = PrefixList.TYPE.value
        return result
    
class SiteList(List):
    TYPE = ListType.SITE
    def to_dict(self):
        result = super().to_dict()
        result[List.TYPE_FIELD] = SiteList.TYPE.value
        return result

class SLAClass(List):
    TYPE = ListType.SLA
    def to_dict(self):
        result = super().to_dict()
        result[List.TYPE_FIELD] = SLAClass.TYPE.value
        return result

class TLOCList(List):
    TYPE = ListType.TLOC
    def to_dict(self):
        result = super().to_dict()
        result[List.TYPE_FIELD] = TLOCList.TYPE.value
        return result

class VPNList(List):
    TYPE = ListType.VPN
    def to_dict(self):
        result = super().to_dict()
        result[List.TYPE_FIELD] = VPNList.TYPE.value
        return result