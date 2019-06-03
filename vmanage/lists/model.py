from vmanage.entity import Model

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
    TYPE = "app"
    def to_dict(self):
        result = super().to_dict()
        result[List.TYPE_FIELD] = ApplicationList.TYPE
        return result

class ColorList(List):
    TYPE = "color"
    def to_dict(self):
        result = super().to_dict()
        result[List.TYPE_FIELD] = ColorList.TYPE
        return result

class DataPrefixList(List):
    TYPE = "dataPrefix"
    def to_dict(self):
        result = super().to_dict()
        result[List.TYPE_FIELD] = DataPrefixList.TYPE
        return result

class Policer(List):
    TYPE = "policer"
    def to_dict(self):
        result = super().to_dict()
        result[List.TYPE_FIELD] = Policer.TYPE
        return result
    
class PrefixList(List):
    TYPE = "prefix"
    def to_dict(self):
        result = super().to_dict()
        result[List.TYPE_FIELD] = PrefixList.TYPE
        return result
    
class SiteList(List):
    TYPE = "site"
    def to_dict(self):
        result = super().to_dict()
        result[List.TYPE_FIELD] = SiteList.TYPE
        return result

class SLAClass(List):
    TYPE = "sla"
    def to_dict(self):
        result = super().to_dict()
        result[List.TYPE_FIELD] = SLAClass.TYPE
        return result

class TLOCList(List):
    TYPE = "tloc"
    def to_dict(self):
        result = super().to_dict()
        result[List.TYPE_FIELD] = TLOCList.TYPE
        return result

class VPNList(List):
    TYPE = "vpn"
    def to_dict(self):
        result = super().to_dict()
        result[List.TYPE_FIELD] = VPNList.TYPE
        return result