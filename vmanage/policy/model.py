from json import JSONDecoder,JSONDecodeError,JSONEncoder
from abc import abstractproperty,abstractmethod

from vmanage.entity import Model,HelperModel,ModelFactory

from vmanage.policy.tool import PolicyType,References,accumulator
from vmanage.policy.tool import DefinitionType,ReferenceType,Definitions

class Policy(Model):
    NAME_FIELD = "policyName"
    NAME_LIMIT = 32
    ID_FIELD = "policyId"
    DESCRIPTION_FIELD = "policyDescription"
    DEFINITION_FIELD = "policyDefinition"
    TYPE_FIELD = "policyType"
    def __init__(self,mid:str,name:str,policy_type:str,description:str):
        super().__init__(mid)
        self.name = name
        self._type = policy_type
        self.description = description
    @property
    def type(self):
        return PolicyType(self._type)
    def to_dict(self):
        return {
            Policy.ID_FIELD : self.id,
            Policy.NAME_FIELD : self.name[:(Policy.NAME_LIMIT - 1)],
            Policy.TYPE_FIELD : self.type.value,
            Policy.DESCRIPTION_FIELD : self.description
        }
    def __str__(self):
        return "{mid} -> '{name}'".format(mid=self.id,name=self.name)

class CLIPolicy(Policy):
    TYPE = PolicyType.CLI
    def __init__(self,mid:str,name:str,policy_type:str,description:str,definition:str):
        super().__init__(mid,name,policy_type,description)
        self.definition = definition
    def to_dict(self):
        result = super().to_dict()
        result[Policy.DEFINITION_FIELD] = self.definition
        return result
    @staticmethod
    def from_dict(document:dict):
        mid = document.get(Policy.ID_FIELD)
        name = document.get(Policy.NAME_FIELD)
        policy_type = document.get(Policy.TYPE_FIELD)
        description = document.get(Policy.DESCRIPTION_FIELD)
        definition = document.get(Policy.DEFINITION_FIELD)
        fields = [mid,name,policy_type,description,definition]
        if all(fields):
            return CLIPolicy(mid,name,policy_type,description,definition)
        return None

class GUIPolicy(Policy):
    TYPE = PolicyType.FEATURE
    ASSEMBLY_FIELD = "assembly"
    def __init__(self,mid:str,name:str,policy_type:str,description:str,definition:dict):
        super().__init__(mid,name,policy_type,description)
        self.definition = definition
    @abstractmethod
    def definitions(self,accumulator:Definitions=None):
        pass
    @property
    def assembly(self):
        return (
            DefinitionApplication(application)
            for application in self.definition.get(GUIPolicy.ASSEMBLY_FIELD)
        )
    def to_dict(self):
        result = super().to_dict()
        result[Policy.DEFINITION_FIELD] = JSONEncoder().encode(self.definition)
        return result
    @classmethod
    def from_dict(cls,document:dict):
        mid = document.get(Policy.ID_FIELD)
        name = document.get(Policy.NAME_FIELD)
        policy_type = document.get(Policy.TYPE_FIELD)
        description = document.get(Policy.DESCRIPTION_FIELD)
        definition = document.get(Policy.DEFINITION_FIELD)
        try:
            definition = JSONDecoder().decode(definition)
        except JSONDecodeError:
            definition = None
        fields = [mid,name,policy_type,description,definition]
        if all(fields):
            return cls(mid,name,policy_type,description,definition)
        return None

class Definition(Model):
    NAME_FIELD = "name"
    NAME_LIMIT = 32
    ID_FIELD = "definitionId"
    DESCRIPTION_FIELD = "description"
    TYPE_FIELD = "type"
    def __init__(self,mid:str,name:str,def_type:str,description:str):
        super().__init__(mid)
        self.name = name
        self._type = def_type
        self.description = description
    @property
    def type(self):
        return DefinitionType(self._type)
    def to_dict(self):
        return {
            Definition.ID_FIELD : self.id,
            Definition.NAME_FIELD : self.name[:Definition.NAME_LIMIT],
            Definition.TYPE_FIELD : self.type.value,
            Definition.DESCRIPTION_FIELD : self.description
        }
    def __str__(self):
        return "{mid} -> '{name}'".format(mid=self.id,name=self.name)

class CommonDefinition(Definition):
    DEFINITION_FIELD = "definition"
    def __init__(self,mid:str,name:str,def_type:str,description:str,definition:dict):
        super().__init__(mid,name,def_type,description)
        self.definition = definition
    def to_dict(self):
        result = super().to_dict()
        result[CommonDefinition.DEFINITION_FIELD] = self.definition 
        return result
    @classmethod
    def from_dict(cls,document:dict):
        mid = document.get(Definition.ID_FIELD)
        name = document.get(Definition.NAME_FIELD)
        def_type = document.get(Definition.TYPE_FIELD)
        description = document.get(Definition.DESCRIPTION_FIELD)
        definition = document.get(CommonDefinition.DEFINITION_FIELD,{})
        fields = [mid,name,def_type,description,definition]
        if all(fields):
            return cls(mid,name,def_type,description,definition)
        return None

class SequencedDefinition(Definition):
    SEQUENCES_FIELD = "sequences"
    def __init__(self,mid:str,name:str,def_type:str,description:str,definition:list):
        super().__init__(mid,name,def_type,description)
        self.definition = definition
    def to_dict(self):
        result = super().to_dict()
        result[SequencedDefinition.SEQUENCES_FIELD] = self.definition
        return result
    @accumulator(References)
    def references(self,accumulator:References=None):
        for sequence in self.sequences:
            sequence.references(accumulator=accumulator)
        return accumulator
    @property
    def sequences(self):
        return (
            DefinitionSequenceElement(sequence) 
            for sequence in self.definition
        )
    @classmethod
    def from_dict(cls,document:dict):
        mid = document.get(Definition.ID_FIELD)
        name = document.get(Definition.NAME_FIELD)
        def_type = document.get(Definition.TYPE_FIELD)
        description = document.get(Definition.DESCRIPTION_FIELD)
        sequences = document.get(SequencedDefinition.SEQUENCES_FIELD,[])
        fields = [mid,name,def_type,description]
        if all(fields):
            return cls(mid,name,def_type,description,sequences)
        return None

class DefinitionSequenceElement(HelperModel):
    TYPE_FIELD = "sequenceType"
    MATCH_FIELD = "match"
    ACTIONS_FIELD = "actions"
    @property
    def type(self):
        return self.definition.get(DefinitionSequenceElement.TYPE_FIELD)
    @accumulator(References)
    def references(self,accumulator:References=None):
        self.match.references(accumulator=accumulator)
        for action in self.actions:
            if isinstance(action,DefinitionUniActionElement) or isinstance(action,DefinitionMultiActionElement):
                action.references(accumulator=accumulator)
        return accumulator
    @property
    def match(self):
        return DefinitionMatchElement(self.definition.get(DefinitionSequenceElement.MATCH_FIELD))
    @property
    def actions(self):
        factory = DefinitionActionElementFactory()
        return (
            factory.from_dict(entry)
            for entry in self.definition.get(DefinitionSequenceElement.ACTIONS_FIELD)
        )

class DefinitionMatchElement(HelperModel):
    ENTRIES_FIELD = "entries"
    @property
    def entries(self):
        factory = DefinitionMatchEntryFactory()
        return (
            factory.from_dict(entry) 
            for entry in self.definition.get(DefinitionMatchElement.ENTRIES_FIELD)
        )
    @accumulator(References)
    def references(self,accumulator:References=None):
        for entry in self.entries:
            if isinstance(entry,DefinitionMatchReferenceEntry):
                entry.references(accumulator=accumulator)
        return accumulator

class DefinitionMatchEntry(HelperModel):  
    FIELDTYPE_FIELD = "field"
    VALUE_FIELD = "value"
    REFERENCE_FIELD = "ref"
    @property
    def type(self):
        return self.definition.get(DefinitionMatchEntry.FIELDTYPE_FIELD)

class DefinitionMatchValuedEntry(DefinitionMatchEntry):
    @property
    def value(self):
        return self.definition.get(DefinitionMatchEntry.VALUE_FIELD)

class DefinitionMatchReferenceEntry(DefinitionMatchEntry):
    @accumulator(References)
    def references(self,accumulator:References=None):
        accumulator.add_by_type(ReferenceType(self.type),self.definition.get(DefinitionMatchEntry.REFERENCE_FIELD))
        return accumulator

class DefinitionMatchEntryFactory:
    def from_dict(self,document:dict):
        if document.get(DefinitionMatchEntry.REFERENCE_FIELD):
            return DefinitionMatchReferenceEntry(document)
        elif document.get(DefinitionMatchEntry.VALUE_FIELD):
            return DefinitionMatchValuedEntry(document)
        raise ValueError("Unsupported Match Entry type: {0}".format(document))

class DefinitionActionElement(HelperModel):
    TYPE_FIELD = "type"
    PARAMETER_FIELD = "parameter"
    @property
    def type(self):
        return self.definition.get(DefinitionActionElement.TYPE_FIELD)

class DefinitionMultiActionElement(DefinitionActionElement):
    @property
    def parameters(self):
        factory = DefinitionActionEntryFactory()
        return (
            factory.from_dict(entry)
            for entry in self.definition.get(DefinitionActionElement.PARAMETER_FIELD)
        )
    @accumulator(References)
    def references(self,accumulator:References=None):
        for param in self.parameters:
            if isinstance(param,DefinitionActionReferenceEntry):
                param.references(accumulator=accumulator)
        return accumulator

class DefinitionUniActionElement(DefinitionActionElement):
    @property
    def parameter(self):
        factory = DefinitionActionEntryFactory()
        return factory.from_dict(self.definition.get(DefinitionActionElement.PARAMETER_FIELD))
    @accumulator(References)
    def references(self,accumulator:References=None):
        if isinstance(self.parameter,DefinitionActionReferenceEntry):
            self.parameter.references(accumulator=accumulator)
        return accumulator

class DefinitionActionElementFactory:
    def from_dict(self,document:dict):
        parameter = document.get(DefinitionActionElement.PARAMETER_FIELD)
        if isinstance(parameter,dict):
            return DefinitionUniActionElement(document)
        elif isinstance(parameter,list):
            return DefinitionMultiActionElement(document)
        return DefinitionActionElement(document)

class DefinitionActionEntry(HelperModel):
    FIELDTYPE_FIELD = "field"
    VALUE_FIELD = "value"
    REFERENCE_FIELD = "ref"
    @property
    def type(self):
        return self.definition.get(DefinitionActionEntry.FIELDTYPE_FIELD)

class DefinitionActionValuedEntry(DefinitionActionEntry):
    @property
    def value(self):
        return self.definition.get(DefinitionActionEntry.VALUE_FIELD)

class DefinitionActionReferenceEntry(DefinitionActionEntry):
    @accumulator(References)
    def references(self,accumulator:References=None):
        accumulator.add_by_type(ReferenceType(self.type),self.definition.get(DefinitionActionEntry.REFERENCE_FIELD))
        return accumulator

class DefinitionActionEntryFactory:
    def from_dict(self,document:dict):
        if document.get(DefinitionActionEntry.REFERENCE_FIELD):
            return DefinitionActionReferenceEntry(document)
        elif document.get(DefinitionActionEntry.VALUE_FIELD):
            return DefinitionActionValuedEntry(document)
        return DefinitionActionEntry(document)

class DefinitionApplication(HelperModel):
    TYPE_FIELD = "type"
    ID_FIELD = "definitionId"
    @property
    def type(self):
        return DefinitionType(self.definition.get(DefinitionApplication.TYPE_FIELD))
    @property
    def id(self):
        return self.definition.get(DefinitionApplication.ID_FIELD)