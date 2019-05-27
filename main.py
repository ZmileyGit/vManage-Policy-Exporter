from vmanage.config import Configuration

from vmanage.auth import vManageSession

from vmanage.entity import Server

from vmanage.policy.centralized.dao import PoliciesDAO,DefinitionDAOFactory

from vmanage.policy.centralized.model import GUIPolicy,HubNSpokeDefinition
from vmanage.policy.centralized.model import MeshDefinition,ControlDefinition
from vmanage.policy.centralized.model import DefinitionMatchReferenceEntry,DefinitionMatchValuedEntry

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
        print("Sequence type: {0}".format(sequence.sequence_type))
        for entry in sequence.match.entries:
            if isinstance(entry,DefinitionMatchReferenceEntry):
                print("Match entry: {0} | Match reference: {1}".format(entry.field_type,entry.reference))
            elif isinstance(entry,DefinitionMatchValuedEntry):
                print("Match entry: {0} | Match value: {1}".format(entry.field_type,entry.value))
            else:
                print(entry)

def extract_policies(server,user,password):
    with vManageSession(server,secure=False) as session:
        if session.login(user,password):
            centralized_policies = PoliciesDAO(session)
            definition_dao_fac = DefinitionDAOFactory(session)
            policies = centralized_policies.get_all()
            for policy in policies:
                if isinstance(policy,GUIPolicy):
                    assembly = policy.assembly
                    print(assembly)
                    for raw_definition in assembly:
                        definition_type = raw_definition.get("type")
                        definition_id = raw_definition.get("definitionId")
                        if definition_type and definition_id:
                            definition = definition_dao_fac.from_type(definition_type).get_by_id(definition_id)
                            if isinstance(definition,HubNSpokeDefinition):
                                pass
                            elif isinstance(definition,MeshDefinition):
                                pass
                            elif isinstance(definition,ControlDefinition):
                                pass

def main():
    config = Configuration.from_file("./config.json")
    extract_policies(config.server,config.username,config.password)

main()