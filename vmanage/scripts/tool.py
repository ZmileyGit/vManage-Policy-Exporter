from vmanage.lists.model import ListFactory
from vmanage.entity import ModelFactory
from re import Match

class PolicyExportFormat:
    POLICIES_FIELD = "policies"
    DEFINITIONS_FIELD = "definitions"
    REFERENCES_FIELD = "references"
    DEFINITION_MAP_FIELD = "definition_map"
    REFERENCE_MAP_FIELD = "reference_map"
    def __init__(self):
        self.policies = set()
        self.definitions = set()
        self.references = set()
        self.definition_map = {}
        self.reference_map = {}
    def to_dict(self):
        return {
            PolicyExportFormat.POLICIES_FIELD : [policy.to_dict() for policy in self.policies],
            PolicyExportFormat.DEFINITIONS_FIELD : [definition.to_dict() for definition in self.definitions],
            PolicyExportFormat.REFERENCES_FIELD : [reference.to_dict() for reference in self.references],
            PolicyExportFormat.DEFINITION_MAP_FIELD : self.definition_map,
            PolicyExportFormat.REFERENCE_MAP_FIELD : self.reference_map
        }
    def __str__(self):
        return str(vars(self))
    @staticmethod
    def from_dict(document:dict,policy_factory:ModelFactory,def_factory:ModelFactory):
        report = PolicyExportFormat()

        raw_policies = document.get(PolicyExportFormat.POLICIES_FIELD,[])
        report.policies.update(policy_factory.from_dict(policy) for policy in raw_policies)

        raw_definitions = document.get(PolicyExportFormat.DEFINITIONS_FIELD,[])
        report.definitions.update(def_factory.from_dict(definition) for definition in raw_definitions)

        raw_references = document.get(PolicyExportFormat.REFERENCES_FIELD,[])
        ref_factory = ListFactory()
        report.references.update(ref_factory.from_dict(reference) for reference in raw_references)

        report.definition_map.update(document.get(PolicyExportFormat.DEFINITION_MAP_FIELD,{}))

        report.reference_map.update(document.get(PolicyExportFormat.REFERENCE_MAP_FIELD,{}))

        return report

class PolicyImportReport:
    def __init__(self):
        self.policies = set()
        self.definitions = set()
        self.references = set()
        self.policy_map = {}
        self.definition_map = {}
        self.reference_map = {}
    def __str__(self):
        return str(vars(self))

def map_sub(map_repl:dict):
    def repl(match:Match):
        return map_repl[match[0]]
    return repl