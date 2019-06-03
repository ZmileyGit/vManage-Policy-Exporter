from vmanage.policy.tool import References,ReferenceType

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
        application_lists = set() if application_lists is None else application_lists
        color_lists = set() if color_lists is None else color_lists
        site_lists = set() if site_lists is None else site_lists
        sla_classes = set() if sla_classes is None else sla_classes
        tloc_lists = set() if tloc_lists is None else tloc_lists
        vpn_lists = set() if vpn_lists is None else vpn_lists
        self.application_lists = application_lists
        self.color_lists = color_lists
        self.site_lists = site_lists
        self.sla_classes = sla_classes
        self.tloc_lists = tloc_lists
        self.vpn_lists = vpn_lists
    def add_by_type(self,ref_type:ReferenceType,reference:str):
        if ref_type == ReferenceType.COLOR_LIST:
            self.color_lists.add(reference)
        elif ref_type == ReferenceType.SITE_LIST:
            self.site_lists.add(reference)
        elif ref_type == ReferenceType.TLOC_LIST:
            self.tloc_lists.add(reference)
        elif ref_type == ReferenceType.VPN_LIST:
            self.vpn_lists.add(reference)
        elif ref_type == ReferenceType.PREFIX_LIST:
            self.prefix_lists.add(reference)
