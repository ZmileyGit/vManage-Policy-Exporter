from enum import Enum

from vmanage.policy.tool import References,ReferenceType,DefinitionType
from vmanage.policy.tool import Definitions
from vmanage.lists.model import ListFactory

class CentralizedReferences(References):
    def __init__(
        self,
        application_lists:set = None,
        color_lists:set = None,
        data_prefix_lists:set = None,
        policers:set = None,
        prefix_lists:set = None,
        site_lists:set = None,
        sla_classes:set = None,
        tloc_lists:set = None,
        vpn_lists:set = None
    ):
        super().__init__(data_prefix_lists=data_prefix_lists,policers=policers,prefix_lists=prefix_lists)
        self.application_lists = set() if application_lists is None else application_lists
        self.color_lists = set() if color_lists is None else color_lists
        self.site_lists = set() if site_lists is None else site_lists
        self.sla_classes = set() if sla_classes is None else sla_classes
        self.tloc_lists = set() if tloc_lists is None else tloc_lists
        self.vpn_lists = set() if vpn_lists is None else vpn_lists
    def as_list(self):
        references = super().as_list()
        references.extend([(ReferenceType.APP_LIST.value,app_list) for app_list in self.application_lists])
        references.extend([(ReferenceType.COLOR_LIST.value,color_list) for color_list in self.color_lists])
        references.extend([(ReferenceType.SITE_LIST.value,site_list) for site_list in self.site_lists])
        references.extend([(ReferenceType.SLA_CLASS.value,sla_class) for sla_class in self.sla_classes])
        references.extend([(ReferenceType.TLOC_LIST.value,tloc_list) for tloc_list in self.tloc_lists])
        references.extend([(ReferenceType.VPN_LIST.value,vpn_list) for vpn_list in self.vpn_lists])
        return references
    def merge(self,source):
        super().merge(source)
        self.application_lists.update(source.application_lists)
        self.color_lists.update(source.color_lists)
        self.site_lists.update(source.site_lists)
        self.sla_classes.update(source.sla_classes)
        self.tloc_lists.update(source.tloc_lists)
        self.vpn_lists.update(source.vpn_lists)
    def add_by_type(self,ref_type:ReferenceType,reference):
        if ref_type == ReferenceType.COLOR_LIST:
            self.color_lists.add(reference)
        elif ref_type == ReferenceType.SITE_LIST:
            self.site_lists.add(reference)
        elif ref_type == ReferenceType.TLOC_LIST:
            self.tloc_lists.add(reference)
        elif ref_type == ReferenceType.VPN_LIST:
            self.vpn_lists.add(reference)
        elif ref_type == ReferenceType.APP_LIST or ref_type == ReferenceType.DNS_APP_LIST:
            self.application_lists.add(reference)
        elif ref_type == ReferenceType.SLA_CLASS:
            self.sla_classes.add(reference)
        else:
            super().add_by_type(ref_type,reference)

class CentralizedDefinitions(Definitions):
    def __init__(
        self,
        hub_n_spoke:set=None,
        mesh:set=None,
        custom_control:set=None,
        vpn_membership:set=None,
        app_route:set=None,
        data:set=None,
        cflowd:set=None
    ):
        self.hub_n_spoke = set() if hub_n_spoke is None else hub_n_spoke
        self.mesh = set() if mesh is None else mesh
        self.custom_control = set() if custom_control is None else custom_control
        self.vpn_membership = set() if vpn_membership is None else vpn_membership
        self.app_route = set() if app_route is None else app_route
        self.data = set() if data is None else data
        self.cflowd = set() if cflowd is None else cflowd
    def merge(self,source):
        self.hub_n_spoke.update(source.hub_n_spoke)
        self.mesh.update(source.mesh)
        self.custom_control.update(source.custom_control)
        self.vpn_membership.update(source.vpn_membership)
        self.app_route.update(source.app_route)
        self.data.update(source.data)
        self.cflowd.update(source.cflowd)
    def as_list(self):
        definitions = []
        definitions.extend([(DefinitionType.HUB_N_SPOKE.value,hub_n_spoke) for hub_n_spoke in self.hub_n_spoke])
        definitions.extend([(DefinitionType.MESH.value,mesh) for mesh in self.mesh])
        definitions.extend([(DefinitionType.CONTROL.value,control) for control in self.custom_control])
        definitions.extend([(DefinitionType.VPN_MEMBERSHIP.value,vpn_membership) for vpn_membership in self.vpn_membership])
        definitions.extend([(DefinitionType.APP_ROUTE.value,app_route) for app_route in self.app_route])
        definitions.extend([(DefinitionType.DATA.value,data) for data in self.data])
        definitions.extend([(DefinitionType.CFLOWD.value,cflowd) for cflowd in self.cflowd])
        return definitions
    def add_by_type(self,def_type:DefinitionType,definition):
        if def_type == DefinitionType.HUB_N_SPOKE:
            self.hub_n_spoke.add(definition)
        elif def_type == DefinitionType.MESH:
            self.mesh.add(definition)
        elif def_type == DefinitionType.CONTROL:
            self.custom_control.add(definition)
        elif def_type == DefinitionType.VPN_MEMBERSHIP:
            self.vpn_membership.add(definition)
        elif def_type == DefinitionType.APP_ROUTE:
            self.app_route.add(definition)
        elif def_type == DefinitionType.DATA:
            self.data.add(definition)
        elif def_type == DefinitionType.CFLOWD:
            self.cflowd.add(definition)
        else:
            raise ValueError("Unsupported Definition Type: {0}".format(def_type))
    def __str__(self):
        return str(vars(self))