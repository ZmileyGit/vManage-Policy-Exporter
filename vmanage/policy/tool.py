from enum import Enum
from abc import ABC,abstractmethod,abstractproperty

class ReferenceType(Enum):
    COLOR_LIST = "colorList"
    SITE_LIST = "siteList"
    TLOC_LIST = "tlocList"
    VPN_LIST = "vpnList"
    PREFIX_LIST = "prefixList"
    APP_LIST = "appList"
    DNS_APP_LIST = "dnsAppList"
    DATA_PREFIX_LIST = "dataPrefixList"
    SOURCE_DATA_PREFIX_LIST = "sourceDataPrefixList"
    DEST_DATA_PREFIX_LIST = "destinationDataPrefixList"
    SLA_CLASS = "slaClass"
    POLICER = "policer"
    FORWARDING_CLASS = "class"
    MIRROR = "mirror"
    AS_PATH = "asPath"
    COMMUNITY = "community"
    EXTENDED_COMMUNITY = "extCommunity"

class PolicyType(Enum):
    CLI = "cli"
    FEATURE = "feature"

class DefinitionType(Enum):
    HUB_N_SPOKE = "hubAndSpoke"
    MESH = "mesh"
    CONTROL = "control"
    VPN_MEMBERSHIP = "vpnMembershipGroup"
    APP_ROUTE = "appRoute"
    DATA = "data"
    CFLOWD = "cflowd"
    QOS_MAP = "qosMap"
    REWRITE_RULE = "rewriteRule"
    ACLv4 = "acl"
    ACLv6 = "aclv6"
    ROUTE_POLICY = "vedgeRoute"

class References:
    def __init__(
        self,
        data_prefix_lists:set = None,
        policers:set = None,
        prefix_lists:set = None
    ):
        self.data_prefix_lists = set() if data_prefix_lists is None else data_prefix_lists
        self.policers = set() if policers is None else policers
        self.prefix_lists = set() if prefix_lists is None else prefix_lists
    def as_list(self):
        references = []
        references.extend([(ReferenceType.DATA_PREFIX_LIST.value,data_pref_list) for data_pref_list in self.data_prefix_lists])
        references.extend([(ReferenceType.POLICER.value,policer) for policer in self.policers])
        references.extend([(ReferenceType.PREFIX_LIST.value,prefix_list) for prefix_list in self.prefix_lists])
        return references
    def merge(self,source):
        self.data_prefix_lists.update(source.data_prefix_lists)
        self.policers.update(source.policers)
        self.prefix_lists.update(source.prefix_lists)
    def add_by_type(self,ref_type:ReferenceType,reference:str):
        if ref_type == ReferenceType.SOURCE_DATA_PREFIX_LIST or ref_type == ReferenceType.DEST_DATA_PREFIX_LIST:
            self.data_prefix_lists.add(reference)
        elif ref_type == ReferenceType.PREFIX_LIST:
            self.prefix_lists.add(reference)
        elif ref_type == ReferenceType.POLICER:
            self.policers.add(reference)
        else:
            raise ValueError("Unsupported Reference Type: {0}".format(ref_type))
    def __str__(self):
        return str(vars(self))

class Definitions(ABC):
    @abstractmethod
    def merge(self,source):
        pass
    @abstractmethod
    def as_list(self):
        pass
    @abstractmethod
    def add_by_type(self,def_type:DefinitionType,definition):
        pass
    def __str__(self):
        return str(vars(self))

def accumulator(klass):
    def accumulator_decorator(func):
        def wrapper(*args,**kwargs):
            key_word = "accumulator"
            if key_word not in kwargs:
                kwargs[key_word] = klass()
            return func(*args,**kwargs)
        return wrapper
    return accumulator_decorator

def factory_memoization(func):
    cache = {}
    def wrapper(*args,**kwargs):
        typed = args[1]
        if typed not in cache:
            cache[typed] = func(*args,**kwargs)
        return cache[typed]
    return wrapper