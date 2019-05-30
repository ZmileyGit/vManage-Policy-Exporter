from vmanage.policy.tool import References

class CentralizedReferences(References):
    def __init__(
        self,
        application_lists:set = set(),
        color_lists:set = set(),
        data_prefix_lists:set = set(),
        policers:set = set(),
        prefix_lists:set = set(),
        site_lists:set = set(),
        sla_classes:set = set(),
        tloc_lists:set = set(),
        vpn_lists:set = set()
    ):
        super().__init__(data_prefix_lists=data_prefix_lists,policers=policers,prefix_lists=prefix_lists)
        self.application_lists = application_lists
        self.color_lists = color_lists
        self.site_lists = site_lists
        self.sla_classes = sla_classes
        self.tloc_lists = tloc_lists
        self.vpn_lists = vpn_lists