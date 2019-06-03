from enum import Enum

class References:
    def __init__(
        self,
        data_prefix_lists:set = None,
        policers:set = None,
        prefix_lists:set = None
    ):
        data_prefix_lists = set() if data_prefix_lists is None else data_prefix_lists
        policers = set() if policers is None else policers
        prefix_lists = set() if prefix_lists is None else prefix_lists
        self.data_prefix_lists = data_prefix_lists
        self.policers = policers
        self.prefix_lists = prefix_lists
    def __str__(self):
        return str(vars(self))

class ReferenceType(Enum):
    COLOR_LIST = "colorList"
    SITE_LIST = "siteList"
    TLOC_LIST = "tlocList"
    VPN_LIST = "vpnList"
    PREFIX_LIST = "prefixList"

def accumulator(klass):
    def accumulator_decorator(func):
        def wrapper(*args,**kwargs):
            key_word = "accumulator"
            if key_word not in kwargs:
                kwargs[key_word] = klass()
            return func(*args,**kwargs)
        return wrapper
    return accumulator_decorator