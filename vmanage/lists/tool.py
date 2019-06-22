from enum import Enum

class ListType(Enum):
    APP = "app"
    COLOR = "color"
    DATA_PREFIX = "dataPrefix"
    POLICER = "policer"
    PREFIX = "prefix"
    SITE = "site"
    SLA = "sla"
    TLOC = "tloc"
    VPN = "vpn"
    AS_PATH = "asPath"
    COMMUNITY = "community"
    EXTENDED_COMMUNITY = "extCommunity"
    FORWARDING_CLASS = "class"
    MIRROR = "mirror"