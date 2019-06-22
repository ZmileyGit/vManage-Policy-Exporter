from vmanage.policy.tool import References,ReferenceType
from vmanage.policy.tool import Definitions,DefinitionType

class LocalizedReferences(References):
    def __init__(
        self,
        as_paths:set = None,
        communities:set = None,
        data_prefix_lists:set = None,
        extended_communities:set = None,
        class_maps:set = None,
        mirrors:set = None,
        policers:set = None,
        prefix_lists:set = None
    ):
        super().__init__(data_prefix_lists=data_prefix_lists,policers=policers,prefix_lists=prefix_lists)
        self.as_paths = set() if as_paths is None else as_paths
        self.communities = set() if communities is None else communities
        self.extended_communities = set() if extended_communities is None else extended_communities
        self.class_maps = set() if class_maps is None else class_maps
        self.mirrors = set() if mirrors is None else mirrors
    def as_list(self):
        references = super().as_list()
        references.extend((ReferenceType.AS_PATH.value,as_path) for as_path in self.as_paths)
        references.extend((ReferenceType.COMMUNITY.value,community) for community in self.communities)
        references.extend((ReferenceType.EXTENDED_COMMUNITY.value,ext_comm) for ext_comm in self.extended_communities)
        references.extend((ReferenceType.FORWARDING_CLASS.value,class_map) for class_map in self.class_maps)
        references.extend((ReferenceType.MIRROR.value,mirror) for mirror in self.mirrors)
        return references
    def merge(self,source):
        super().merge(source)
        self.as_paths.update(source.as_paths)
        self.communities.update(source.communities)
        self.extended_communities.update(source.extended_communities)
        self.class_maps.update(source.class_maps)
        self.mirrors.update(source.mirrors)
    def add_by_type(self,ref_type:ReferenceType,reference):
        if ref_type == ReferenceType.AS_PATH:
            self.as_paths.add(reference)
        elif ref_type == ReferenceType.COMMUNITY:
            self.communities.add(reference)
        elif ref_type == ReferenceType.EXTENDED_COMMUNITY:
            self.extended_communities.add(reference)
        elif ref_type == ReferenceType.FORWARDING_CLASS:
            self.class_maps.add(reference)
        elif ref_type == ReferenceType.MIRROR:
            self.mirrors.add(reference)
        else:
            super().add_by_type(ref_type,reference)

class LocalizedDefinitions(Definitions):
    def __init__(
        self,
        qos_map:set = None,
        rewrite_rule:set = None,
        aclv4:set = None,
        aclv6:set = None,
        vedge_route:set = None
    ):
        self.qos_map = set() if qos_map is None else qos_map
        self.rewrite_rule = set() if rewrite_rule is None else rewrite_rule
        self.aclv4 = set() if aclv4 is None else aclv4
        self.aclv6 = set() if aclv6 is None else aclv6
        self.vedge_route = set() if vedge_route is None else vedge_route
    def merge(self,source):
        self.qos_map.update(source.qos_map)
        self.rewrite_rule.update(source.rewrite_rule)
        self.aclv4.update(source.aclv4)
        self.aclv6.update(source.aclv6)
        self.vedge_route.update(source.vedge_route)
    def as_list(self):
        definitions = []
        definitions.extend((DefinitionType.QOS_MAP.value,qos_map) for qos_map in self.qos_map)
        definitions.extend((DefinitionType.REWRITE_RULE.value,rew_rule) for rew_rule in self.rewrite_rule)
        definitions.extend((DefinitionType.ACLv4.value,aclv4) for aclv4 in self.aclv4)
        definitions.extend((DefinitionType.ACLv6.value,aclv6) for aclv6 in self.aclv6)
        definitions.extend((DefinitionType.ROUTE_POLICY.value,vroute) for vroute in self.vedge_route)
        return definitions
    def add_by_type(self,def_type:DefinitionType,definition):
        if def_type == DefinitionType.QOS_MAP:
            self.qos_map.add(definition)
        elif def_type == DefinitionType.REWRITE_RULE:
            self.rewrite_rule.add(definition)
        elif def_type == DefinitionType.ACLv4:
            self.aclv4.add(definition)
        elif def_type == DefinitionType.ACLv6:
            self.aclv6.add(definition)
        elif def_type == DefinitionType.ROUTE_POLICY:
            self.vedge_route.add(definition)
        else:
            raise ValueError("Unsupported Definition Type: {0}".format(def_type))