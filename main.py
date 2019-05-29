from vmanage.config import Configuration

from vmanage.auth import vManageSession

from vmanage.entity import Server

from vmanage.policy.centralized.dao import PoliciesDAO,DefinitionDAOFactory

from vmanage.policy.centralized.model import GUIPolicy,HubNSpokeDefinition
from vmanage.policy.centralized.model import MeshDefinition,ControlDefinition
from vmanage.policy.centralized.model import DefinitionMatchReferenceEntry,DefinitionMatchValuedEntry
from vmanage.policy.centralized.model import DefinitionMultiActionElement,DefinitionUniActionElement
from vmanage.policy.centralized.model import DefinitionActionReferenceEntry,DefinitionActionValuedEntry

def hub_n_spoke_test(definition:HubNSpokeDefinition):
    print("VPN list: {0}".format(definition.vpn_list))
    for subdef in definition.sub_definitions:
        print("TLOC list: {0}".format(subdef.tloc_list))
        for spoke in subdef.spokes:
            print("Spoke Site list: {0}".format(spoke.site_list))
            for hub in spoke.hubs:
                print("Hub Site list: {0}".format(hub.site_list))
                for prefix in hub.prefix_lists:
                    print("Hub Prefix list: {0}".format(prefix))

def mesh_test(definition:MeshDefinition):
    print("VPN list: {0}".format(definition.vpn_list))
    for region in definition.regions:
        for site in region.site_lists:
            print("Region Site list: {0}".format(site))

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
                            hub_n_spoke_test(definition)
                        elif isinstance(definition,MeshDefinition):
                            mesh_test(definition)
                        elif isinstance(definition,ControlDefinition):
                            control_test(definition)

def main():
    config = Configuration.from_file("./config.json")
    extract_policies(config.server,config.username,config.password)

main()