from vmanage.entity import HelperModel,Model,ModelFactory

from vmanage.policy.centralized.tool import CentralizedReferences,CentralizedDefinitions
from vmanage.policy.centralized.tool import DefinitionType,PolicyType
from vmanage.policy.tool import accumulator,ReferenceType

from json import JSONDecoder,JSONDecodeError,JSONEncoder

class Policy(Model):
    NAME_FIELD = "policyName"
    NAME_LIMIT = 32
    ID_FIELD = "policyId"
    DESCRIPTION_FIELD = "policyDescription"
    DEFINITION_FIELD = "policyDefinition"
    TYPE_FIELD = "policyType"
    def __init__(self,mid:str,name:str,policy_type:str,description:str):
        super().__init__(mid)
        self.name = name
        self._type = policy_type
        self.description = description
    @property
    def type(self):
        return PolicyType(self._type)
    def to_dict(self):
        return {
            Policy.ID_FIELD : self.id,
            Policy.NAME_FIELD : self.name[:Policy.NAME_LIMIT],
            Policy.TYPE_FIELD : self.type.value,
            Policy.DESCRIPTION_FIELD : self.description
        }
    def __str__(self):
        return "{mid} -> '{name}'".format(mid=self.id,name=self.name)

class CLIPolicy(Policy):
    TYPE = PolicyType.CLI
    def __init__(self,mid:str,name:str,policy_type:str,description:str,definition:str):
        super().__init__(mid,name,policy_type,description)
        self.definition = definition
    def to_dict(self):
        result = super().to_dict()
        result[Policy.DEFINITION_FIELD] = self.definition
        return result
    @staticmethod
    def from_dict(document:dict):
        mid = document.get(Policy.ID_FIELD)
        name = document.get(Policy.NAME_FIELD)
        policy_type = document.get(Policy.TYPE_FIELD)
        description = document.get(Policy.DESCRIPTION_FIELD)
        definition = document.get(Policy.DEFINITION_FIELD)
        fields = [mid,name,policy_type,description,definition]
        if all(fields):
            return CLIPolicy(mid,name,policy_type,description,definition)
        return None

class GUIPolicy(Policy):
    TYPE = PolicyType.FEATURE
    ASSEMBLY_FIELD = "assembly"
    def __init__(self,mid:str,name:str,policy_type:str,description:str,definition:dict):
        super().__init__(mid,name,policy_type,description)
        self.definition = definition
    @accumulator(CentralizedReferences)
    def references(self,accumulator:CentralizedReferences=None):
        for application in self.assembly:
            if isinstance(application,DefinitionReferenceApplication):
                application.references(accumulator=accumulator)
        return accumulator
    @accumulator(CentralizedDefinitions)
    def definitions(self,accumulator:CentralizedDefinitions=None):
        for application in self.assembly:
            accumulator.add_by_type(application.type,application.id)
        return accumulator
    @property
    def assembly(self):
        factory = DefinitionApplicationFactory()
        return (
            factory.from_dict(entry)
            for entry in self.definition.get(GUIPolicy.ASSEMBLY_FIELD)
        )
    def to_dict(self):
        result = super().to_dict()
        result[Policy.DEFINITION_FIELD] = JSONEncoder().encode(self.definition)
        return result
    @staticmethod
    def from_dict(document:dict):
        mid = document.get(Policy.ID_FIELD)
        name = document.get(Policy.NAME_FIELD)
        policy_type = document.get(Policy.TYPE_FIELD)
        description = document.get(Policy.DESCRIPTION_FIELD)
        definition = document.get(Policy.DEFINITION_FIELD)
        try:
            definition = JSONDecoder().decode(definition)
        except JSONDecodeError:
            definition = None
        fields = [mid,name,policy_type,description,definition]
        if all(fields):
            return GUIPolicy(mid,name,policy_type,description,definition)
        return None

class PolicyFactory(ModelFactory):
    def from_dict(self,document:dict):
        policy_type = PolicyType(document.get(Policy.TYPE_FIELD))
        if policy_type == PolicyType.CLI:
            return CLIPolicy.from_dict(document)
        elif policy_type == PolicyType.FEATURE:
            return GUIPolicy.from_dict(document)
        return None

class Definition(Model):
    NAME_FIELD = "name"
    NAME_LIMIT = 32
    ID_FIELD = "definitionId"
    DESCRIPTION_FIELD = "description"
    TYPE_FIELD = "type"
    def __init__(self,mid:str,name:str,def_type:str,description:str):
        super().__init__(mid)
        self.name = name
        self._type = def_type
        self.description = description
    @property
    def type(self):
        return DefinitionType(self._type)
    def to_dict(self):
        return {
            Definition.ID_FIELD : self.id,
            Definition.NAME_FIELD : self.name[:Definition.NAME_LIMIT],
            Definition.TYPE_FIELD : self.type.value,
            Definition.DESCRIPTION_FIELD : self.description
        }
    def __str__(self):
        return "{mid} -> '{name}'".format(mid=self.id,name=self.name)

class CommonDefinition(Definition):
    DEFINITION_FIELD = "definition"
    def __init__(self,mid:str,name:str,def_type:str,description:str,definition:dict):
        super().__init__(mid,name,def_type,description)
        self.definition = definition
    def to_dict(self):
        result = super().to_dict()
        result[CommonDefinition.DEFINITION_FIELD] = self.definition 
        return result
    @classmethod
    def from_dict(cls,document:dict):
        mid = document.get(Definition.ID_FIELD)
        name = document.get(Definition.NAME_FIELD)
        def_type = document.get(Definition.TYPE_FIELD)
        description = document.get(Definition.DESCRIPTION_FIELD)
        definition = document.get(CommonDefinition.DEFINITION_FIELD,{})
        fields = [mid,name,def_type,description,definition]
        if all(fields):
            return cls(mid,name,def_type,description,definition)
        return None

class SequencedDefinition(Definition):
    SEQUENCES_FIELD = "sequences"
    def __init__(self,mid:str,name:str,def_type:str,description:str,definition:list):
        super().__init__(mid,name,def_type,description)
        self.definition = definition
    def to_dict(self):
        result = super().to_dict()
        result[SequencedDefinition.SEQUENCES_FIELD] = self.definition
        return result
    @accumulator(CentralizedReferences)
    def references(self,accumulator:CentralizedReferences=None):
        for sequence in self.sequences:
            sequence.references(accumulator=accumulator)
        return accumulator
    @property
    def sequences(self):
        return (
            DefinitionSequenceElement(sequence) 
            for sequence in self.definition
        )
    @classmethod
    def from_dict(cls,document:dict):
        mid = document.get(Definition.ID_FIELD)
        name = document.get(Definition.NAME_FIELD)
        def_type = document.get(Definition.TYPE_FIELD)
        description = document.get(Definition.DESCRIPTION_FIELD)
        sequences = document.get(SequencedDefinition.SEQUENCES_FIELD,[])
        fields = [mid,name,def_type,description]
        if all(fields):
            return cls(mid,name,def_type,description,sequences)
        return None

class DefinitionSequenceElement(HelperModel):
    TYPE_FIELD = "sequenceType"
    MATCH_FIELD = "match"
    ACTIONS_FIELD = "actions"
    @property
    def type(self):
        return self.definition.get(DefinitionSequenceElement.TYPE_FIELD)
    @accumulator(CentralizedReferences)
    def references(self,accumulator:CentralizedReferences=None):
        self.match.references(accumulator=accumulator)
        for action in self.actions:
            if isinstance(action,DefinitionMultiActionElement) or isinstance(action,DefinitionUniActionElement):
                action.references(accumulator=accumulator)
        return accumulator
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
    def parameters(self):
        factory = DefinitionActionEntryFactory()
        return (
            factory.from_dict(entry)
            for entry in self.definition.get(DefinitionActionElement.PARAMETER_FIELD)
        )
    @accumulator(CentralizedReferences)
    def references(self,accumulator:CentralizedReferences=None):
        for param in self.parameters:
            if isinstance(param,DefinitionActionReferenceEntry) or isinstance(param,DefinitionActionServiceEntry):
                param.references(accumulator=accumulator)
        return accumulator


class DefinitionSLAClassActionElement(DefinitionMultiActionElement):
    TYPE = "slaClass"
    @property
    def parameters(self):
        factory = DefinitionSLAClassActionEntryFactory()
        return (
            factory.from_dict(entry)
            for entry in self.definition.get(DefinitionActionElement.PARAMETER_FIELD)
        )

class DefinitionUniActionElement(DefinitionActionElement):
    @property
    def parameter(self):
        factory = DefinitionActionEntryFactory()
        return factory.from_dict(self.definition.get(DefinitionActionElement.PARAMETER_FIELD))
    @accumulator(CentralizedReferences)
    def references(self,accumulator:CentralizedReferences=None):
        if isinstance(self.parameter,DefinitionActionReferenceEntry) or isinstance(self.parameter,DefinitionActionServiceEntry):
            self.parameter.references(accumulator=accumulator)
        return accumulator

class DefinitionActionElementFactory:
    def from_dict(self,document:dict):
        parameter = document.get(DefinitionActionElement.PARAMETER_FIELD)
        action_type = document.get(DefinitionActionElement.TYPE_FIELD)
        if action_type == DefinitionSLAClassActionElement.TYPE:
            return DefinitionSLAClassActionElement(document)
        elif isinstance(parameter,dict):
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
    @accumulator(CentralizedReferences)
    def references(self,accumulator:CentralizedReferences=None):
        if isinstance(self.service,ReferenceActionService):
            self.service.references(accumulator=accumulator)
        return accumulator

class DefinitionActionReferenceEntry(DefinitionActionEntry):
    @accumulator(CentralizedReferences)
    def references(self,accumulator:CentralizedReferences=None):
        accumulator.add_by_type(ReferenceType(self.type),self.definition.get(DefinitionActionEntry.REFERENCE_FIELD))
        return accumulator
        
class DefinitionSLAClassActionEntry(DefinitionActionReferenceEntry):
    @accumulator(CentralizedReferences)
    def references(self,accumulator:CentralizedReferences=None):
        accumulator.add_by_type(ReferenceType.SLA_CLASS,self.definition.get(DefinitionActionEntry.REFERENCE_FIELD))
        return accumulator

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

class DefinitionSLAClassActionEntryFactory(DefinitionActionEntryFactory):
    def from_dict(self,document:dict):
        action_type = document.get(DefinitionActionEntry.FIELDTYPE_FIELD)
        if action_type == "name":
            return DefinitionSLAClassActionEntry(document)
        return super().from_dict(document)

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
    @accumulator(CentralizedReferences)
    def references(self,accumulator:CentralizedReferences=None):
        accumulator.tloc_lists.add(self.tloc_list)
        return accumulator
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
    @accumulator(CentralizedReferences)
    def references(self,accumulator:CentralizedReferences=None):
        for entry in self.entries:
            if isinstance(entry,DefinitionMatchReferenceEntry):
                entry.references(accumulator=accumulator)
        return accumulator

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
    @accumulator(CentralizedReferences)
    def references(self,accumulator:CentralizedReferences=None):
        accumulator.add_by_type(ReferenceType(self.type),self.definition.get(DefinitionMatchEntry.REFERENCE_FIELD))
        return accumulator

class DefinitionMatchEntryFactory:
    def from_dict(self,document:dict):
        if document.get(DefinitionMatchEntry.REFERENCE_FIELD):
            return DefinitionMatchReferenceEntry(document)
        elif document.get(DefinitionMatchEntry.VALUE_FIELD):
            return DefinitionMatchValuedEntry(document)
        else:
            return DefinitionMatchEntry(document)

class HubNSpokeDefinition(CommonDefinition):
    TYPE = DefinitionType.HUB_N_SPOKE
    SUBDEFINITIONS_FIELD = "subDefinitions"
    VPNLIST_FIELD = "vpnList"
    @accumulator(CentralizedReferences)
    def references(self,accumulator:CentralizedReferences=None):
        accumulator.vpn_lists.add(self.vpn_list)
        for subdef in self.sub_definitions:
            subdef.references(accumulator=accumulator)
        return accumulator
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
    @accumulator(CentralizedReferences)
    def references(self,accumulator:CentralizedReferences=None):
        if self.tloc_list:
            accumulator.tloc_lists.add(self.tloc_list)
        for spoke in self.spokes:
            spoke.references(accumulator=accumulator)
        return accumulator

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
    @accumulator(CentralizedReferences)
    def references(self,accumulator:CentralizedReferences=None):
        accumulator.site_lists.add(self.site_list)
        for hub in self.hubs:
            hub.references(accumulator=accumulator)
        return accumulator

class HubNSpokeHubElement(HelperModel):
    SITELIST_FIELD = "siteList"
    PREFIXLIST_FIELD = "prefixLists"
    @property
    def site_list(self):
        return self.definition.get(HubNSpokeHubElement.SITELIST_FIELD)
    @property
    def prefix_lists(self):
        return self.definition.get(HubNSpokeHubElement.PREFIXLIST_FIELD,[])
    @accumulator(CentralizedReferences)
    def references(self,accumulator:CentralizedReferences=None):
        accumulator.site_lists.add(self.site_list)
        accumulator.prefix_lists.update(self.prefix_lists)
        return accumulator

class MeshDefinition(CommonDefinition):
    TYPE = DefinitionType.MESH
    REGIONS_FIELD = "regions"
    VPNLIST_FIELD = "vpnList"
    @accumulator(CentralizedReferences)
    def references(self,accumulator:CentralizedReferences=None):
        accumulator.vpn_lists.add(self.vpn_list)
        for region in self.regions:
            region.references(accumulator=accumulator)
        return accumulator
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
    @accumulator(CentralizedReferences)
    def references(self,accumulator:CentralizedReferences=None):
        accumulator.site_lists.update(self.site_lists)
        return accumulator

class ControlDefinition(SequencedDefinition):
    TYPE = DefinitionType.CONTROL
    def to_dict(self):
        result = super().to_dict()
        result[Definition.TYPE_FIELD] = ControlDefinition.TYPE.value
        return result

class VPNMembershipDefinition(CommonDefinition):
    TYPE = DefinitionType.VPN_MEMBERSHIP
    SITES_FIELD = "sites"
    @accumulator(CentralizedReferences)
    def references(self,accumulator:CentralizedReferences=None):
        for site in self.sites:
            site.references(accumulator=accumulator)
        return accumulator
    @property
    def sites(self):
        return (
            VPNMembershipSiteElement(site) 
            for site in self.definition[VPNMembershipDefinition.SITES_FIELD]
        )

class VPNMembershipSiteElement(HelperModel):
    SITELIST_FIELD = "siteList"
    VPNLISTS_FIELD = "vpnList"
    @accumulator(CentralizedReferences)
    def references(self,accumulator:CentralizedReferences=None):
        accumulator.site_lists.add(self.site_list)
        accumulator.vpn_lists.update(self.vpn_lists)
        return accumulator
    @property
    def site_list(self):
        return self.definition[VPNMembershipSiteElement.SITELIST_FIELD]
    @property
    def vpn_lists(self):
        return self.definition[VPNMembershipSiteElement.VPNLISTS_FIELD]

class AppRouteDefinition(SequencedDefinition):
    TYPE = DefinitionType.APP_ROUTE

class DataDefinition(SequencedDefinition):
    TYPE = DefinitionType.DATA

class CflowdDefinition(CommonDefinition):
    TYPE = DefinitionType.CFLOWD

class DefinitionFactory:
    def from_dict(self,document:dict):
        doc_type = DefinitionType(document.get(Definition.TYPE_FIELD))
        if doc_type == DefinitionType.HUB_N_SPOKE:
            return HubNSpokeDefinition.from_dict(document)
        elif doc_type == DefinitionType.MESH:
            return MeshDefinition.from_dict(document)
        elif doc_type == DefinitionType.CONTROL:
            return ControlDefinition.from_dict(document)
        elif doc_type == DefinitionType.VPN_MEMBERSHIP:
            return VPNMembershipDefinition.from_dict(document)
        elif doc_type == DefinitionType.APP_ROUTE:
            return AppRouteDefinition.from_dict(document)
        elif doc_type == DefinitionType.DATA:
            return DataDefinition.from_dict(document)
        elif doc_type == DefinitionType.CFLOWD:
            return CflowdDefinition.from_dict(document)
        raise ValueError("Unsupported Definition Type: {0}".format(doc_type))

class DefinitionApplication(HelperModel):
    TYPE_FIELD = "type"
    ID_FIELD = "definitionId"
    ENTRIES_FIELD = "entries"
    @property
    def type(self):
        return DefinitionType(self.definition.get(DefinitionApplication.TYPE_FIELD))
    @property
    def id(self):
        return self.definition.get(DefinitionApplication.ID_FIELD)

class DefinitionReferenceApplication(DefinitionApplication):
    @property
    def entries(self):
        return []
    @accumulator(CentralizedReferences)
    def references(self,accumulator:CentralizedReferences=None):
        for entry in self.entries:
            entry.references(accumulator=accumulator)
        return accumulator

class ControlPolicyApplication(DefinitionReferenceApplication):
    DEFINITION = ControlDefinition
    @property
    def entries(self):
        return (
            ControlDirectionApplication(entry)
            for entry in self.definition.get(DefinitionApplication.ENTRIES_FIELD)
        )

class ControlDirectionApplication(HelperModel):
    DIRECTION_FIELD = "direction"
    SITELISTS_FIELD = "siteLists"
    @property
    def direction(self):
        return self.definition.get(ControlDirectionApplication.DIRECTION_FIELD)
    @property
    def site_lists(self):
        return self.definition.get(ControlDirectionApplication.SITELISTS_FIELD,[])
    @accumulator(CentralizedReferences)
    def references(self,accumulator:CentralizedReferences=None):
        accumulator.site_lists.update(self.site_lists)
        return accumulator

class DataPolicyApplication(DefinitionReferenceApplication):
    DEFINITION = DataDefinition
    @property
    def entries(self):
        return (
            DataDirectionApplication(entry)
            for entry in self.definition.get(DefinitionApplication.ENTRIES_FIELD)
        )

class DataDirectionApplication(HelperModel):
    DIRECTION_FIELD = "direction"
    SITELISTS_FIELD = "siteLists"
    VPNLISTS_FIELD = "vpnLists"
    @property
    def direction(self):
        return self.definition.get(DataDirectionApplication.DIRECTION_FIELD)
    @property
    def site_lists(self):
        return self.definition.get(DataDirectionApplication.SITELISTS_FIELD,[])
    @property
    def vpn_lists(self):
        return self.definition.get(DataDirectionApplication.VPNLISTS_FIELD,[])
    @accumulator(CentralizedReferences)
    def references(self,accumulator:CentralizedReferences=None):
        accumulator.site_lists.update(self.site_lists)
        accumulator.vpn_lists.update(self.vpn_lists)
        return accumulator

class CflowdPolicyApplication(DefinitionReferenceApplication):
    DEFINITION = CflowdDefinition
    @property
    def entries(self):
        return (
            CflowdApplicationEntry(entry)
            for entry in self.definition.get(DefinitionApplication.ENTRIES_FIELD)
        )

class CflowdApplicationEntry(HelperModel):
    SITELISTS_FIELD = "siteLists"
    @property
    def site_lists(self):
        return self.definition.get(CflowdApplicationEntry.SITELISTS_FIELD,[])
    @accumulator(CentralizedReferences)
    def references(self,accumulator:CentralizedReferences=None):
        accumulator.site_lists.update(self.site_lists)
        return accumulator

class AppRoutePolicyApplication(DefinitionReferenceApplication):
    DEFINITION = AppRouteDefinition
    @property
    def entries(self):
        return (
            AppRouteApplicationEntry(entry)
            for entry in self.definition.get(DefinitionApplication.ENTRIES_FIELD)
        )
    
class AppRouteApplicationEntry(HelperModel):
    SITELISTS_FIELD = "siteLists"
    VPNLISTS_FIELD = "vpnLists"
    @property
    def site_lists(self):
        return self.definition.get(AppRouteApplicationEntry.SITELISTS_FIELD,[])
    @property
    def vpn_lists(self):
        return self.definition.get(AppRouteApplicationEntry.VPNLISTS_FIELD,[])
    @accumulator(CentralizedReferences)
    def references(self,accumulator:CentralizedReferences=None):
        accumulator.site_lists.update(self.site_lists)
        accumulator.vpn_lists.update(self.vpn_lists)
        return accumulator

class DefinitionApplicationFactory:
    def from_dict(self,document:dict):
        doc_type = DefinitionType(document.get(DefinitionApplication.TYPE_FIELD))
        if doc_type == ControlDefinition.TYPE:
            return ControlPolicyApplication(document)
        elif doc_type == DataDefinition.TYPE:
            return DataPolicyApplication(document)
        elif doc_type == CflowdDefinition.TYPE:
            return CflowdPolicyApplication(document)
        elif doc_type == AppRouteDefinition.TYPE:
            return AppRoutePolicyApplication(document)
        return DefinitionApplication(document)