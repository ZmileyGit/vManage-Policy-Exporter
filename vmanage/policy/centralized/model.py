from vmanage.entity import HelperModel,Model,ModelFactory
from json import JSONDecoder,JSONDecodeError

class CentralizedPolicy(Model):
    NAME_FIELD = "policyName"
    ID_FIELD = "policyId"
    DESCRIPTION_FIELD = "policyDescription"
    DEFINITION_FIELD = "policyDefinition"
    TYPE_FIELD = "policyType"
    def __init__(self,mid:str,name:str,description:str):
        super().__init__(mid)
        self.name = name
        self.description = description
    def to_dict(self):
        return {
            CentralizedPolicy.ID_FIELD : self.id,
            CentralizedPolicy.NAME_FIELD : self.name,
            CentralizedPolicy.DESCRIPTION_FIELD : self.description
        }
    def __str__(self):
        return "{mid} -> '{name}'".format(mid=self.id,name=self.name)

class CentralizedCLIPolicy(CentralizedPolicy):
    POLICY_TYPE = "cli"
    def __init__(self,mid:str,name:str,description:str,definition:str):
        super().__init__(mid,name,description)
        self.definition = definition
    def to_dict(self):
        result = super().to_dict()
        result[CentralizedPolicy.TYPE_FIELD] = CentralizedCLIPolicy.POLICY_TYPE
        result[CentralizedPolicy.DEFINITION_FIELD] = self.definition
        return result
    @staticmethod
    def from_dict(document:dict):
        mid = document.get(CentralizedPolicy.ID_FIELD)
        name = document.get(CentralizedPolicy.NAME_FIELD)
        description = document.get(CentralizedPolicy.DESCRIPTION_FIELD)
        definition = document.get(CentralizedPolicy.DEFINITION_FIELD)
        fields = [mid,name,description,definition]
        if all(fields):
            return CentralizedCLIPolicy(mid,name,description,definition)
        return None

class CentralizedGUIPolicy(CentralizedPolicy):
    POLICY_TYPE = "feature"
    def __init__(self,mid:str,name:str,description:str,definition:dict):
        super().__init__(mid,name,description)
        self.definition = definition
    def to_dict(self):
        result = super().to_dict()
        result[CentralizedPolicy.TYPE_FIELD] = CentralizedGUIPolicy.TYPE_FIELD
        result[CentralizedPolicy.DEFINITION_FIELD] = self.definition
        return result
    @staticmethod
    def from_dict(document:dict):
        mid = document.get(CentralizedPolicy.ID_FIELD)
        name = document.get(CentralizedPolicy.NAME_FIELD)
        description = document.get(CentralizedPolicy.DESCRIPTION_FIELD)
        definition = document.get(CentralizedPolicy.DEFINITION_FIELD)
        try:
            definition = JSONDecoder().decode(definition)
        except JSONDecodeError:
            definition = None
        fields = [mid,name,description,definition]
        if all(fields):
            return CentralizedGUIPolicy(mid,name,description,definition)
        return None

class CentralizedPolicyFactory(ModelFactory):
    def from_dict(self,document:dict):
        policy_type = document.get(CentralizedPolicy.TYPE_FIELD)
        if policy_type == CentralizedCLIPolicy.POLICY_TYPE:
            return CentralizedCLIPolicy.from_dict(document)
        elif policy_type == CentralizedGUIPolicy.POLICY_TYPE:
            return CentralizedGUIPolicy.from_dict(document)
        return None

class CentralizedDefinition(Model):
    NAME_FIELD = "name"
    ID_FIELD = "definitionId"
    DESCRIPTION_FIELD = "description"
    TYPE_FIELD = "type"
    def __init__(self,mid:str,name:str,description:str):
        super().__init__(mid)
        self.name = name
        self.description = description
    def to_dict(self):
        return {
            CentralizedDefinition.ID_FIELD : self.id,
            CentralizedDefinition.NAME_FIELD : self.name,
            CentralizedDefinition.DESCRIPTION_FIELD : self.description
        }
    def __str__(self):
        return "{mid} -> '{name}'".format(mid=self.id,name=self.name)

class CentralizedCommonDefinition(CentralizedDefinition):
    DEFINITION_FIELD = "definition"
    def __init__(self,mid:str,name:str,description:str,definition:dict):
        super().__init__(mid,name,description)
        self.definition = definition
    def to_dict(self):
        result = super().to_dict()
        result[CentralizedCommonDefinition.DEFINITION_FIELD] = self.definition 
        return result
    @classmethod
    def from_dict(cls,document:dict):
        mid = document.get(CentralizedDefinition.ID_FIELD)
        name = document.get(CentralizedDefinition.NAME_FIELD)
        description = document.get(CentralizedDefinition.DESCRIPTION_FIELD)
        definition = document.get(CentralizedCommonDefinition.DEFINITION_FIELD)
        fields = [mid,name,description,definition]
        if all(fields):
            return cls(mid,name,description,definition)
        return None

class CentralizedSequencedDefinition(CentralizedDefinition):
    SEQUENCES_FIELD = "sequences"
    def __init__(self,mid:str,name:str,description:str,sequences:dict):
        super().__init__(mid,name,description)
        self._sequences = sequences
    def to_dict(self):
        result = super().to_dict()
        result[CentralizedSequencedDefinition.SEQUENCES_FIELD] = self._sequences
        return result
    @property
    def sequences(self):
        return [DefinitionSequenceElement(sequence) for sequence in self._sequences]
    @classmethod
    def from_dict(cls,document:dict):
        mid = document.get(CentralizedDefinition.ID_FIELD)
        name = document.get(CentralizedDefinition.NAME_FIELD)
        description = document.get(CentralizedDefinition.DESCRIPTION_FIELD)
        sequences = document.get(CentralizedSequencedDefinition.SEQUENCES_FIELD,[])
        fields = [mid,name,description]
        if all(fields):
            return cls(mid,name,description,sequences)
        return None

class DefinitionSequenceElement(HelperModel):
    TYPE_FIELD = "sequenceType"
    MATCH_FIELD = "match"
    ACTIONS_FIELD = "actions"
    @property
    def sequence_type(self):
        return self.definition.get(DefinitionSequenceElement.TYPE_FIELD)
    @property
    def match(self):
        return DefinitionMatchElement(self.definition.get(DefinitionSequenceElement.MATCH_FIELD))
    @property
    def actions(self):
        return self.definition.get(DefinitionSequenceElement.ACTIONS_FIELD)

class DefinitionMatchElement(HelperModel):
    ENTRIES_FIELD = "entries"
    FIELDTYPE_FIELD = "field"
    VALUE_FIELD = "value"
    REFERENCE_FIELD = "ref"
    @property
    def entries(self):
        result = []
        for entry in self.definition.get(DefinitionMatchElement.ENTRIES_FIELD,[]):
            if entry.get(DefinitionMatchElement.REFERENCE_FIELD):
                result.append(DefinitionMatchReferenceEntry(entry))
            elif entry.get(DefinitionMatchElement.VALUE_FIELD):
                result.append(DefinitionMatchValuedEntry(entry))
            else:
                result.append(DefinitionMatchEntry(entry))
        return result

class DefinitionMatchEntry(HelperModel):  
    @property
    def field_type(self):
        return self.definition.get(DefinitionMatchElement.FIELDTYPE_FIELD)

class DefinitionMatchValuedEntry(DefinitionMatchEntry):
    @property
    def value(self):
        return self.definition.get(DefinitionMatchElement.VALUE_FIELD)

class DefinitionMatchReferenceEntry(DefinitionMatchEntry):
    @property
    def reference(self):
        return self.definition.get(DefinitionMatchElement.REFERENCE_FIELD)

class HubNSpokeDefinition(CentralizedCommonDefinition):
    DEFINITION_TYPE = "hubAndSpoke"
    SUBDEFINITIONS_FIELD = "subDefinitions"
    VPNLIST_FIELD = "vpnList"
    def to_dict(self):
        result = super().to_dict()
        result[CentralizedDefinition.TYPE_FIELD] = HubNSpokeDefinition.DEFINITION_TYPE
        return result
    @property
    def vpn_list(self):
        return self.definition.get(HubNSpokeDefinition.VPNLIST_FIELD)
    @property
    def sub_definitions(self):
        return [HubNSpokeSubDefinition(definition) 
                for definition in self.definition.get(HubNSpokeDefinition.SUBDEFINITIONS_FIELD)]

class HubNSpokeSubDefinition(HelperModel):
    SPOKES_FIELD = "spokes"
    TLOCLIST_FIELD = "tlocList"
    @property
    def spokes(self):
        return [HubNSpokeSpokeElement(definition)
            for definition in self.definition.get(HubNSpokeSubDefinition.SPOKES_FIELD)]
    @property
    def tloc_list(self):
        return self.definition.get(HubNSpokeSubDefinition.TLOCLIST_FIELD)

class HubNSpokeSpokeElement(HelperModel):
    SITELIST_FIELD = "siteList"
    HUBS_FIELD = "hubs"
    @property
    def site_list(self):
        return self.definition.get(HubNSpokeSpokeElement.SITELIST_FIELD)
    @property
    def hubs(self):
        return [HubNSpokeHubElement(definition)
        for definition in self.definition.get(HubNSpokeSpokeElement.HUBS_FIELD)]

class HubNSpokeHubElement(HelperModel):
    SITELIST_FIELD = "siteList"
    PREFIXLIST_FIELD = "prefixLists"
    @property
    def site_list(self):
        return self.definition.get(HubNSpokeHubElement.SITELIST_FIELD)
    @property
    def prefix_lists(self):
        return self.definition.get(HubNSpokeHubElement.PREFIXLIST_FIELD)

class MeshDefinition(CentralizedCommonDefinition):
    DEFINITION_TYPE = "mesh"
    REGIONS_FIELD = "regions"
    VPNLIST_FIELD = "vpnList"
    def to_dict(self):
        result = super().to_dict()
        result[CentralizedDefinition.TYPE_FIELD] = MeshDefinition.DEFINITION_TYPE
        return result
    @property
    def vpn_list(self):
        return self.definition.get(MeshDefinition.VPNLIST_FIELD)
    @property
    def regions(self):
        return [MeshRegionElement(definition)
        for definition in self.definition.get(MeshDefinition.REGIONS_FIELD)]
    
class MeshRegionElement(HelperModel):
    SITELISTS_FIELD = "siteLists"
    @property
    def site_lists(self):
        return self.definition.get(MeshRegionElement.SITELISTS_FIELD)

class ControlDefinition(CentralizedSequencedDefinition):
    DEFINITION_TYPE = "control"
    def to_dict(self):
        result = super().to_dict()
        result[CentralizedDefinition.TYPE_FIELD] = ControlDefinition.DEFINITION_TYPE
        return result