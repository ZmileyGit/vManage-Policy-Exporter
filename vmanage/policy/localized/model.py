from vmanage.entity import ModelFactory,HelperModel

from vmanage.policy.model import Policy,GUIPolicy,CLIPolicy
from vmanage.policy.model import CommonDefinition,SequencedDefinition
from vmanage.policy.model import DefinitionSequenceElement
from vmanage.policy.model import DefinitionMatchElement
from vmanage.policy.model import DefinitionMatchReferenceEntry,DefinitionMatchEntry
from vmanage.policy.model import DefinitionMatchEntryFactory
from vmanage.policy.model import DefinitionUniActionElement,DefinitionMultiActionElement
from vmanage.policy.model import DefinitionActionElementFactory,DefinitionActionElement
from vmanage.policy.model import DefinitionActionEntry
from vmanage.policy.tool import PolicyType,accumulator
from vmanage.policy.tool import DefinitionType,ReferenceType

from vmanage.policy.localized.tool import LocalizedReferences,LocalizedDefinitions

class LocalizedGUIPolicy(GUIPolicy):
    @accumulator(LocalizedDefinitions)
    def definitions(self,accumulator:LocalizedDefinitions=None):
        for definition in self.assembly:
            accumulator.add_by_type(definition.type,definition.id)
        return accumulator
    
class PolicyFactory(ModelFactory):
    def from_dict(self,document):
        def_type = PolicyType(document.get(Policy.TYPE_FIELD))
        if def_type == PolicyType.CLI:
            return CLIPolicy.from_dict(document)
        elif def_type == PolicyType.FEATURE:
            return LocalizedGUIPolicy.from_dict(document)
        raise ValueError("Unsupported Policy Type: {0}".format(def_type))

class QoSMapDefinition(CommonDefinition):
    TYPE = DefinitionType.QOS_MAP

class RewriteRuleDefinition(CommonDefinition):
    TYPE = DefinitionType.REWRITE_RULE
    RULES_FIELD = "rules"
    @accumulator(LocalizedReferences)
    def references(self,accumulator:LocalizedReferences=None):
        for rule in self.rules:
            rule.references(accumulator=accumulator)
        return accumulator
    @property
    def rules(self):
        return (
            RewriteRuleElement(rule)
            for rule in self.definition.get(RewriteRuleDefinition.RULES_FIELD,[])
        )

class RewriteRuleElement(HelperModel):
    FORWARDING_CLASS_FIELD = "class"
    PLP_FIELD = "plp"
    DSCP_FIELD = "dscp"
    COS_FIELD = "layer2Cos"
    @accumulator(LocalizedReferences)
    def references(self,accumulator:LocalizedReferences=None):
        if self.forwarding_class:
            accumulator.class_maps.add(self.forwarding_class)
        return accumulator
    @property
    def forwarding_class(self):
        return self.definition.get(RewriteRuleElement.FORWARDING_CLASS_FIELD)
    @property
    def plp(self):
        return self.definition.get(RewriteRuleElement.PLP_FIELD)
    @property
    def dscp(self):
        return self.definition.get(RewriteRuleElement.DSCP_FIELD)
    @property
    def cos(self):
        return self.definition.get(RewriteRuleElement.COS_FIELD)

class LocalizedSequencedDefinition(SequencedDefinition):
    @property
    def sequences(self):
        factory = LocalizedSequenceElementFactory()
        return (
            factory.from_dict(sequence)
            for sequence in self.definition
        )
    @accumulator(LocalizedReferences)
    def references(self,accumulator:LocalizedReferences=None):
        for sequence in self.sequences:
            sequence.references(accumulator=accumulator)
        return accumulator

class LocalizedSequenceElement(DefinitionSequenceElement):
    @property
    def actions(self):
        factory = LocalizedActionElementFactory()
        return (
            factory.from_dict(action)
            for action in self.definition.get(DefinitionSequenceElement.ACTIONS_FIELD)
        )

class LocalizedReferenceActionElement(DefinitionUniActionElement):
    @property
    def parameter(self):
        return DefinitionActionEntry(self.definition.get(DefinitionActionElement.PARAMETER_FIELD))
    @accumulator(LocalizedReferences)
    def references(self,accumulator:LocalizedReferences=None):
        reference = self.parameter.definition.get(DefinitionActionEntry.REFERENCE_FIELD)
        if reference:
            accumulator.add_by_type(ReferenceType(self.type),reference)
        return accumulator

class LocalizedActionElementFactory(DefinitionActionElementFactory):
    def __init__(self):
        self._values = {enval.value for enval in ReferenceType.__members__.values()}
    def from_dict(self,document:dict):
        action_type = document.get(DefinitionActionElement.TYPE_FIELD)
        if action_type in self._values:
            return LocalizedReferenceActionElement(document)
        return super().from_dict(document)

class vEdgeRouteSequenceElement(LocalizedSequenceElement):
    TYPE = "vedgeRoute"
    @property
    def match(self):
        return vEdgeRouteMatchElement(self.definition.get(DefinitionSequenceElement.MATCH_FIELD))

class LocalizedSequenceElementFactory:
    def from_dict(self,document:dict):
        sequence_type = document.get(DefinitionSequenceElement.TYPE_FIELD)
        if sequence_type == vEdgeRouteSequenceElement.TYPE:
            return vEdgeRouteSequenceElement(document)
        return LocalizedSequenceElement(document)

class vEdgeRouteMatchElement(DefinitionMatchElement):
    @property
    def entries(self):
        factory = vEdgeRouteMatchEntryFactory()
        return (
            factory.from_dict(entry)
            for entry in self.definition.get(DefinitionMatchElement.ENTRIES_FIELD)
        )

class vEdgeRoutePrefixListMatchEntry(DefinitionMatchReferenceEntry):
    TYPE = "address"
    @accumulator(LocalizedReferences)
    def references(self,accumulator:LocalizedReferences=None):
        accumulator.add_by_type(ReferenceType.PREFIX_LIST,self.definition.get(DefinitionMatchReferenceEntry.REFERENCE_FIELD))
        return accumulator

class vEdgeRouteMatchEntryFactory(DefinitionMatchEntryFactory):
    def from_dict(self,document:dict):
        field_type = document.get(DefinitionMatchEntry.FIELDTYPE_FIELD)
        if field_type == vEdgeRoutePrefixListMatchEntry.TYPE:
            return vEdgeRoutePrefixListMatchEntry(document)
        return super().from_dict(document)

class ACLv4Definition(LocalizedSequencedDefinition):
    TYPE = DefinitionType.ACLv4

class ACLv6Definition(LocalizedSequencedDefinition):
    TYPE = DefinitionType.ACLv6

class vEdgeRouteDefinition(LocalizedSequencedDefinition):
    TYPE = DefinitionType.ROUTE_POLICY