from vmanage.entity import HelperModel,Model,ModelFactory
from json import JSONDecoder,JSONDecodeError

class Policy(Model):
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
            Policy.ID_FIELD : self.id,
            Policy.NAME_FIELD : self.name,
            Policy.DESCRIPTION_FIELD : self.description
        }
    def __str__(self):
        return "{mid} -> '{name}'".format(mid=self.id,name=self.name)

class CLIPolicy(Policy):
    POLICY_TYPE = "cli"
    def __init__(self,mid:str,name:str,description:str,definition:str):
        super().__init__(mid,name,description)
        self.definition = definition
    def to_dict(self):
        result = super().to_dict()
        result[Policy.TYPE_FIELD] = CLIPolicy.POLICY_TYPE
        result[Policy.DEFINITION_FIELD] = self.definition
        return result
    @staticmethod
    def from_dict(document:dict):
        mid = document.get(Policy.ID_FIELD)
        name = document.get(Policy.NAME_FIELD)
        description = document.get(Policy.DESCRIPTION_FIELD)
        definition = document.get(Policy.DEFINITION_FIELD)
        fields = [mid,name,description,definition]
        if all(fields):
            return CLIPolicy(mid,name,description,definition)
        return None

class GUIPolicy(Policy):
    POLICY_TYPE = "feature"
    ASSEMBLY_FIELD = "assembly"
    def __init__(self,mid:str,name:str,description:str,definition:dict):
        super().__init__(mid,name,description)
        self.definition = definition
    @property
    def assembly(self):
        return self.definition.get(GUIPolicy.ASSEMBLY_FIELD)
    def to_dict(self):
        result = super().to_dict()
        result[Policy.TYPE_FIELD] = GUIPolicy.TYPE_FIELD
        result[Policy.DEFINITION_FIELD] = self.definition
        return result
    @staticmethod
    def from_dict(document:dict):
        mid = document.get(Policy.ID_FIELD)
        name = document.get(Policy.NAME_FIELD)
        description = document.get(Policy.DESCRIPTION_FIELD)
        definition = document.get(Policy.DEFINITION_FIELD)
        try:
            definition = JSONDecoder().decode(definition)
        except JSONDecodeError:
            definition = None
        fields = [mid,name,description,definition]
        if all(fields):
            return GUIPolicy(mid,name,description,definition)
        return None

class PolicyFactory(ModelFactory):
    def from_dict(self,document:dict):
        policy_type = document.get(Policy.TYPE_FIELD)
        if policy_type == CLIPolicy.POLICY_TYPE:
            return CLIPolicy.from_dict(document)
        elif policy_type == GUIPolicy.POLICY_TYPE:
            return GUIPolicy.from_dict(document)
        return None

class DefinitionApplicationElement(HelperModel):
    TYPE_FIELD = "type"
    ID_FIELD = "definitionId"
    @property
    def type(self):
        return self.definition.get(DefinitionApplicationElement.TYPE_FIELD)
    @property
    def id(self):
        return self.definition.get(DefinitionApplicationElement.ID_FIELD)

class Definition(Model):
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
            Definition.ID_FIELD : self.id,
            Definition.NAME_FIELD : self.name,
            Definition.DESCRIPTION_FIELD : self.description
        }
    def __str__(self):
        return "{mid} -> '{name}'".format(mid=self.id,name=self.name)

class CommonDefinition(Definition):
    DEFINITION_FIELD = "definition"
    def __init__(self,mid:str,name:str,description:str,definition:dict):
        super().__init__(mid,name,description)
        self.definition = definition
    def to_dict(self):
        result = super().to_dict()
        result[CommonDefinition.DEFINITION_FIELD] = self.definition 
        return result
    @classmethod
    def from_dict(cls,document:dict):
        mid = document.get(Definition.ID_FIELD)
        name = document.get(Definition.NAME_FIELD)
        description = document.get(Definition.DESCRIPTION_FIELD)
        definition = document.get(CommonDefinition.DEFINITION_FIELD)
        fields = [mid,name,description,definition]
        if all(fields):
            return cls(mid,name,description,definition)
        return None

class SequencedDefinition(Definition):
    SEQUENCES_FIELD = "sequences"
    def __init__(self,mid:str,name:str,description:str,sequences:dict):
        super().__init__(mid,name,description)
        self._sequences = sequences
    def to_dict(self):
        result = super().to_dict()
        result[SequencedDefinition.SEQUENCES_FIELD] = self._sequences
        return result
    @property
    def sequences(self):
        return [DefinitionSequenceElement(sequence) for sequence in self._sequences]
    @classmethod
    def from_dict(cls,document:dict):
        mid = document.get(Definition.ID_FIELD)
        name = document.get(Definition.NAME_FIELD)
        description = document.get(Definition.DESCRIPTION_FIELD)
        sequences = document.get(SequencedDefinition.SEQUENCES_FIELD,[])
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

class HubNSpokeDefinition(CommonDefinition):
    DEFINITION_TYPE = "hubAndSpoke"
    SUBDEFINITIONS_FIELD = "subDefinitions"
    VPNLIST_FIELD = "vpnList"
    def to_dict(self):
        result = super().to_dict()
        result[Definition.TYPE_FIELD] = HubNSpokeDefinition.DEFINITION_TYPE
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

class MeshDefinition(CommonDefinition):
    DEFINITION_TYPE = "mesh"
    REGIONS_FIELD = "regions"
    VPNLIST_FIELD = "vpnList"
    def to_dict(self):
        result = super().to_dict()
        result[Definition.TYPE_FIELD] = MeshDefinition.DEFINITION_TYPE
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

class ControlDefinition(SequencedDefinition):
    DEFINITION_TYPE = "control"
    def to_dict(self):
        result = super().to_dict()
        result[Definition.TYPE_FIELD] = ControlDefinition.DEFINITION_TYPE
        return result