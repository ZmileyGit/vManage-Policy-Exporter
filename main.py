from vmanage.config import Configuration

from vmanage.auth import vManageSession

from vmanage.entity import Server

from vmanage.policy.centralized.dao import PoliciesDAO,DefinitionDAOFactory

from vmanage.policy.centralized.model import GUIPolicy,HubNSpokeDefinition
from vmanage.policy.centralized.model import MeshDefinition,ControlDefinition
from vmanage.policy.centralized.model import DefinitionMatchReferenceEntry,DefinitionMatchValuedEntry
from vmanage.policy.centralized.model import DefinitionMultiActionElement,DefinitionUniActionElement
from vmanage.policy.centralized.model import DefinitionActionReferenceEntry,DefinitionActionValuedEntry

def control_test(definition:ControlDefinition):
    for sequence in definition.sequences:
        print("Sequence type: {0}".format(sequence.type))
        print("---Matches---")
        for entry in sequence.match.entries:
            print(entry)
        print("---Actions---")
        for action in sequence.actions:
            print("Action type: {0}".format(action.type))
            if isinstance(action,DefinitionMultiActionElement):
                for entry in action.parameter:
                    print(entry)
            elif isinstance(action,DefinitionUniActionElement):
                entry = action.parameter
                print(entry)
            else:
                print(action)
            

def extract_policies(server,user,password):
    with vManageSession(server,secure=False) as session:
        if session.login(user,password):
            centralized_policies = PoliciesDAO(session)
            definition_dao_fac = DefinitionDAOFactory(session)
            policies = centralized_policies.get_all()
            for policy in policies:
                if isinstance(policy,GUIPolicy):
                    assembly = policy.assembly
                    for application in assembly:
                        print("\n{klass} | {0}".format(application.type,klass=type(application).__name__))
                        definition = definition_dao_fac.from_type(application.type).get_by_id(application.id)
                        if isinstance(definition,HubNSpokeDefinition):
                            print(definition.definition)
                            print(definition.references)
                        elif isinstance(definition,MeshDefinition):
                            print(definition.definition)
                            print(definition.references)
                        elif isinstance(definition,ControlDefinition):
                            control_test(definition)

def main():
    config = Configuration.from_file("./config.json")
    extract_policies(config.server,config.username,config.password)

main()