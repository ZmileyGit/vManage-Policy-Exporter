class References:
    def __init__(
        self,
        data_prefix_lists:set = set(),
        policers:set = set(),
        prefix_lists:set = set()
    ):
        self.data_prefix_lists = data_prefix_lists
        self.policers = policers
        self.prefix_lists = prefix_lists
    def __str__(self):
        return str(vars(self))