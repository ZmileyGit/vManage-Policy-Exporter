from vmanage.entity import HelperModel,Model,ModelFactory

from vmanage.policy.centralized.tool import CentralizedReferences

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
        factory = DefinitionApplicationFactory()
        return (
            factory.from_dict(entry)
            for entry in self.definition.get(GUIPolicy.ASSEMBLY_FIELD)
        )
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

class DefinitionApplication(HelperModel):
    TYPE_FIELD = "type"
    ID_FIELD = "definitionId"
    ENTRIES_FIELD = "entries"
    @property
    def type(self):
        return self.definition.get(DefinitionApplication.TYPE_FIELD)
    @property
    def id(self):
        return self.definition.get(DefinitionApplication.ID_FIELD)

class ControlPolicyApplication(DefinitionApplication):
    TYPE = "control"
    @property
    def entries(self):
        return (ControlDirectionApplication(entry)
                for entry in self.definition.get(DefinitionApplication.ENTRIES_FIELD))

class ControlDirectionApplication(HelperModel):
    DIRECTION_FIELD = "direction"
    SITELIST_FIELD = "siteLists"
    @property
    def direction(self):
        return self.definition.get(ControlDirectionApplication.DIRECTION_FIELD)
    @property
    def site_lists(self):
        return self.definition.get(ControlDirectionApplication.SITELIST_FIELD)

class DefinitionApplicationFactory:
    def from_dict(self,document:dict):
        doc_type = document.get(DefinitionApplication.TYPE_FIELD)
        if doc_type == ControlPolicyApplication.TYPE:
            return ControlPolicyApplication(document)
        else:
            return DefinitionApplication(document)

class Definition(Model):
    NAME_FIELD = "name"
    ID_FIELD = "definitionId"
    DESCRIPTION_FIELD = "description"
    TYPE_FIELD = "type"
    def __init__(self,mid:str,name:str,description:str):
        super().__init__(mid)
        self.name = name
        self.description = description
    def sto_dict(self):
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
        return (
            DefinitionSequenceElement(sequence) 
            for sequence in self._sequences
        )
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
    def type(self):
        return self.definition.get(DefinitionSequenceElement.TYPE_FIELD)
    @property
    def match(self):
        return DefinitionMatchElement(self.definition.get(DefinitionSequenceElement.MATCH_FIELD))
    @property
    def actions(self):
        factory = DefinitionActionElementFactory()
        return (
            factory.from_dict(entry)
            for entry in self.definition.get(DefinitionSequenceElement.ACTIONS_FIELD)
        )

class DefinitionActionElement(HelperModel):
    TYPE_FIELD = "type"
    PARAMETER_FIELD = "parameter"
    @property
    def type(self):
        return self.definition.get(DefinitionActionElement.TYPE_FIELD)

class DefinitionMultiActionElement(DefinitionActionElement):
    @property
    def parameter(self):
        factory = DefinitionActionEntryFactory()
        return (
            factory.from_dict(entry)
            for entry in self.definition.get(DefinitionActionElement.PARAMETER_FIELD)
        )

class DefinitionUniActionElement(DefinitionActionElement):
    @property
    def parameter(self):
        factory = DefinitionActionEntryFactory()
        return factory.from_dict(self.definition.get(DefinitionActionElement.PARAMETER_FIELD))

class DefinitionActionElementFactory:
    def from_dict(self,document:dict):
        parameter = document.get(DefinitionActionElement.PARAMETER_FIELD)
        if isinstance(parameter,dict):
            return DefinitionUniActionElement(document)
        elif isinstance(parameter,list):
            return DefinitionMultiActionElement(document)
        return DefinitionActionElement(document)

class DefinitionActionEntry(HelperModel):
    FIELDTYPE_FIELD = "field"
    VALUE_FIELD = "value"
    REFERENCE_FIELD = "ref"
    @property
    def type(self):
        return self.definition.get(DefinitionActionEntry.FIELDTYPE_FIELD)

class DefinitionActionValuedEntry(DefinitionActionEntry):
    @property
    def value(self):
        return self.definition.get(DefinitionActionEntry.VALUE_FIELD)

class DefinitionActionServiceEntry(DefinitionActionValuedEntry):
    TYPE = "service"
    @property
    def service(self):
        factory = ActionServiceFactory()
        return factory.from_dict(self.value)

class DefinitionActionReferenceEntry(DefinitionActionEntry):
    @property
    def reference(self):
        return self.definition.get(DefinitionActionEntry.REFERENCE_FIELD)

class DefinitionActionEntryFactory:
    def from_dict(self,document:dict):
        action_type = document.get(DefinitionActionEntry.FIELDTYPE_FIELD)
        if action_type == DefinitionActionServiceEntry.TYPE:
            return DefinitionActionServiceEntry(document)
        elif document.get(DefinitionActionEntry.REFERENCE_FIELD):
            return DefinitionActionReferenceEntry(document)
        elif document.get(DefinitionActionEntry.VALUE_FIELD):
            return DefinitionActionValuedEntry(document)
        return DefinitionActionEntry(document)

class ActionService(HelperModel):
    TYPE_FIELD = "type"
    VPN_FIELD = "vpn"
    TLOC_FIELD = "tloc"
    TLOC_LIST_FIELD = "tlocList"
    @property
    def type(self):
        return self.definition.get(ActionService.TYPE_FIELD)
    @property
    def vpn(self):
        return self.definition.get(ActionService.VPN_FIELD)

class ReferenceActionService(ActionService):
    REFERENCE_VALUE = "ref"
    @property
    def tloc_list(self):
        return self.definition.get(ActionService.TLOC_LIST_FIELD,{}).get(ReferenceActionService.REFERENCE_VALUE)

class ValuedActionService(ActionService):
    @property
    def tloc(self):
        self.definition.get(ActionService.TLOC_FIELD)

class ActionServiceFactory:
    def from_dict(self,document:dict):
        if document.get(ActionService.TLOC_FIELD):
            return ValuedActionService(document)
        elif document.get(ActionService.TLOC_LIST_FIELD):
            return ReferenceActionService(document)
        return ActionService(document)

class DefinitionMatchElement(HelperModel):
    ENTRIES_FIELD = "entries"
    @property
    def entries(self):
        factory = DefinitionMatchEntryFactory()
        return (
            factory.from_dict(entry) 
            for entry in self.definition.get(DefinitionMatchElement.ENTRIES_FIELD)
        )

class DefinitionMatchEntry(HelperModel):  
    FIELDTYPE_FIELD = "field"
    VALUE_FIELD = "value"
    REFERENCE_FIELD = "ref"
    @property
    def type(self):
        return self.definition.get(DefinitionMatchEntry.FIELDTYPE_FIELD)

class DefinitionMatchValuedEntry(DefinitionMatchEntry):
    @property
    def value(self):
        return self.definition.get(DefinitionMatchEntry.VALUE_FIELD)

class DefinitionMatchReferenceEntry(DefinitionMatchEntry):
    @property
    def reference(self):
        return self.definition.get(DefinitionMatchEntry.REFERENCE_FIELD)

class DefinitionMatchEntryFactory:
    def from_dict(self,document:dict):
        if document.get(DefinitionMatchEntry.REFERENCE_FIELD):
            return DefinitionMatchReferenceEntry(document)
        elif document.get(DefinitionMatchEntry.VALUE_FIELD):
            return DefinitionMatchValuedEntry(document)
        else:
            return DefinitionMatchEntry(document)

class HubNSpokeDefinition(CommonDefinition):
    DEFINITION_TYPE = "hubAndSpoke"
    SUBDEFINITIONS_FIELD = "subDefinitions"
    VPNLIST_FIELD = "vpnList"
    def to_dict(self):
        result = super().to_dict()
        result[Definition.TYPE_FIELD] = HubNSpokeDefinition.DEFINITION_TYPE
        return result
    @property
    def references(self):
        vpn_lists = set()
        vpn_lists.add(self.vpn_list)

        tloc_lists = set()
        site_lists = set()
        prefix_lists = set()
        for subdef in self.sub_definitions:
            tloc_lists.add(subdef.tloc_list)
            for spoke in subdef.spokes:
                site_lists.add(spoke.site_list)
                for hub in spoke.hubs:
                    site_lists.add(hub.site_list)
                    for prefix in hub.prefix_lists:
                        prefix_lists.add(prefix)
        return CentralizedReferences(vpn_lists=vpn_lists,tloc_lists=tloc_lists,site_lists=site_lists,prefix_lists=prefix_lists)
    @property
    def vpn_list(self):
        return self.definition.get(HubNSpokeDefinition.VPNLIST_FIELD)
    @property
    def sub_definitions(self):
        return (
            HubNSpokeSubDefinition(definition) 
            for definition in self.definition.get(HubNSpokeDefinition.SUBDEFINITIONS_FIELD)
        )

class HubNSpokeSubDefinition(HelperModel):
    SPOKES_FIELD = "spokes"
    TLOCLIST_FIELD = "tlocList"
    @property
    def spokes(self):
        return (
            HubNSpokeSpokeElement(definition)
            for definition in self.definition.get(HubNSpokeSubDefinition.SPOKES_FIELD,[])
        )
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
        return (
            HubNSpokeHubElement(definition)
            for definition in self.definition.get(HubNSpokeSpokeElement.HUBS_FIELD,[])
        )

class HubNSpokeHubElement(HelperModel):
    SITELIST_FIELD = "siteList"
    PREFIXLIST_FIELD = "prefixLists"
    @property
    def site_list(self):
        return self.definition.get(HubNSpokeHubElement.SITELIST_FIELD)
    @property
    def prefix_lists(self):
        return self.definition.get(HubNSpokeHubElement.PREFIXLIST_FIELD,[])

class MeshDefinition(CommonDefinition):
    DEFINITION_TYPE = "mesh"
    REGIONS_FIELD = "regions"
    VPNLIST_FIELD = "vpnList"
    def to_dict(self):
        result = super().to_dict()
        result[Definition.TYPE_FIELD] = MeshDefinition.DEFINITION_TYPE
        return result
    @property
    def references(self):
        vpn_lists = set()
        vpn_lists.add(self.vpn_list)

        site_lists = set()
        for region in self.regions:
            for site in region.site_lists:
                site_lists.add(site)
        return CentralizedReferences(vpn_lists=vpn_lists,site_lists=site_lists)
    @property
    def vpn_list(self):
        return self.definition.get(MeshDefinition.VPNLIST_FIELD)
    @property
    def regions(self):
        return (MeshRegionElement(definition)
        for definition in self.definition.get(MeshDefinition.REGIONS_FIELD,[]))
    
class MeshRegionElement(HelperModel):
    SITELISTS_FIELD = "siteLists"
    @property
    def site_lists(self):
        return self.definition.get(MeshRegionElement.SITELISTS_FIELD,[])

class ControlDefinition(SequencedDefinition):
    DEFINITION_TYPE = "control"
    def to_dict(self):
        result = super().to_dict()
        result[Definition.TYPE_FIELD] = ControlDefinition.DEFINITION_TYPE
        return result