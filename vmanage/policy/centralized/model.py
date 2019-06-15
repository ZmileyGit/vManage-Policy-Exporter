from abc import abstractproperty

from vmanage.entity import HelperModel,Model,ModelFactory

from vmanage.policy.model import Definition,CommonDefinition,SequencedDefinition
from vmanage.policy.model import Policy,GUIPolicy,CLIPolicy
from vmanage.policy.model import DefinitionApplication,SequencedDefinition
from vmanage.policy.model import DefinitionSequenceElement
from vmanage.policy.model import DefinitionActionElementFactory
from vmanage.policy.model import DefinitionMultiActionElement,DefinitionUniActionElement,DefinitionActionElement
from vmanage.policy.model import DefinitionActionEntry,DefinitionActionValuedEntry,DefinitionActionEntryFactory
from vmanage.policy.model import DefinitionActionReferenceEntry
from vmanage.policy.tool import DefinitionType,PolicyType
from vmanage.policy.tool import accumulator,ReferenceType

from vmanage.policy.centralized.tool import CentralizedReferences,CentralizedDefinitions

class CentralizedGUIPolicy(GUIPolicy):
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

class PolicyFactory(ModelFactory):
    def from_dict(self,document:dict):
        policy_type = PolicyType(document.get(Policy.TYPE_FIELD))
        if policy_type == PolicyType.CLI:
            return CLIPolicy.from_dict(document)
        elif policy_type == PolicyType.FEATURE:
            return CentralizedGUIPolicy.from_dict(document)
        raise ValueError("Unsupported Policy Type: {0}".format(policy_type))

class CentralizedSequencedDefinition(SequencedDefinition):
    @property
    def sequences(self):
        return (
            CentralizedSequenceElement(sequence) 
            for sequence in self.definition
        )

class CentralizedSequenceElement(DefinitionSequenceElement):
    @property
    def actions(self):
        factory = CentralizedActionElementFactory()
        return (
            factory.from_dict(entry)
            for entry in self.definition.get(DefinitionSequenceElement.ACTIONS_FIELD)
        )

class CentralizedDefUniActionElement(DefinitionUniActionElement):
    @property
    def parameter(self):
        factory = CentralizedActionEntryFactory()
        return factory.from_dict(self.definition.get(DefinitionActionElement.PARAMETER_FIELD))
    @accumulator(CentralizedReferences)
    def references(self,accumulator:CentralizedReferences=None):
        if isinstance(self.parameter,DefinitionActionServiceEntry):
            self.parameter.references(accumulator=accumulator)
        super().references(accumulator=accumulator)
        return accumulator

class CentralizedDefMultiActionElement(DefinitionMultiActionElement):
    @property
    def parameters(self):
        factory = CentralizedActionEntryFactory()
        return (
            factory.from_dict(entry)
            for entry in self.definition.get(DefinitionActionElement.PARAMETER_FIELD)
        )
    @accumulator(CentralizedReferences)
    def references(self,accumulator:CentralizedReferences=None):
        for param in self.parameters:
            if isinstance(param,DefinitionActionServiceEntry):
                param.references(accumulator=accumulator)
        super().references(accumulator=accumulator)
        return accumulator

class SLAClassActionElement(CentralizedDefMultiActionElement):
    TYPE = "slaClass"
    @property
    def parameters(self):
        factory = DefinitionSLAClassActionEntryFactory()
        return (
            factory.from_dict(entry)
            for entry in self.definition.get(DefinitionActionElement.PARAMETER_FIELD)
        )

class CentralizedActionElementFactory(DefinitionActionElementFactory):
    def from_dict(self,document:dict):
        action_type = document.get(DefinitionActionElement.TYPE_FIELD)
        parameter = document.get(DefinitionActionElement.PARAMETER_FIELD)
        if action_type == SLAClassActionElement.TYPE:
            return SLAClassActionElement(document)
        elif isinstance(parameter,dict):
            return CentralizedDefUniActionElement(document)
        elif isinstance(parameter,list):
            return CentralizedDefMultiActionElement(document)
        return super().from_dict(document)

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

class CentralizedActionEntryFactory(DefinitionActionEntryFactory):
    def from_dict(self,document:dict):
        action_type = document.get(DefinitionActionEntry.FIELDTYPE_FIELD)
        if action_type == DefinitionActionServiceEntry.TYPE:
            return DefinitionActionServiceEntry(document)
        return super().from_dict(document)

class DefinitionSLAClassActionEntry(DefinitionActionReferenceEntry):
    @accumulator(CentralizedReferences)
    def references(self,accumulator:CentralizedReferences=None):
        accumulator.add_by_type(ReferenceType.SLA_CLASS,self.definition.get(DefinitionActionEntry.REFERENCE_FIELD))
        return accumulator

class DefinitionSLAClassActionEntryFactory(CentralizedActionEntryFactory):
    def from_dict(self,document:dict):
        action_type = document.get(DefinitionActionEntry.FIELDTYPE_FIELD)
        if action_type == "name":
            return DefinitionSLAClassActionEntry(document)
        return super().from_dict(document)

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

class ControlDefinition(CentralizedSequencedDefinition):
    TYPE = DefinitionType.CONTROL

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

class AppRouteDefinition(CentralizedSequencedDefinition):
    TYPE = DefinitionType.APP_ROUTE

class DataDefinition(CentralizedSequencedDefinition):
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

class DefinitionReferenceApplication(DefinitionApplication):
    ENTRIES_FIELD = "entries"
    @abstractproperty
    def entries(self):
        pass
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
            for entry in self.definition.get(DefinitionReferenceApplication.ENTRIES_FIELD)
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
            for entry in self.definition.get(DefinitionReferenceApplication.ENTRIES_FIELD)
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
            for entry in self.definition.get(DefinitionReferenceApplication.ENTRIES_FIELD)
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
            for entry in self.definition.get(DefinitionReferenceApplication.ENTRIES_FIELD)
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