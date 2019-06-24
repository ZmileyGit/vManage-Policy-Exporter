import json

from vmanage.config import Configuration

from vmanage.auth import vManageSession

from vmanage.entity import Server

from vmanage.scripts.tool import PolicyExportFormat

from vmanage.policy.tool import ReferenceType

from vmanage.lists.dao import ListDAOFactory

from vmanage.policy.centralized.dao import DefinitionDAOFactory
from vmanage.policy.centralized.model import CflowdDefinition

from vmanage.policy.centralized.dao import PoliciesDAO
from vmanage.policy.centralized.tool import CentralizedReferences,CentralizedDefinitions
from vmanage.policy.centralized.tool import DefinitionType
from vmanage.policy.centralized.model import CentralizedGUIPolicy

def extract_policies(session:vManageSession):
    centralized_policies = PoliciesDAO(session)
    policies = centralized_policies.get_all()
    global_definitions = CentralizedDefinitions()
    global_references = CentralizedReferences()
    report = PolicyExportFormat()
    policy_count = len(policies)
    print("Retrieving Centralized Polices...")
    for count,policy in enumerate(policies):
        print("[{count}/{total}] {policy}".format(count=count + 1,total=policy_count,policy=policy))
        if isinstance(policy,CentralizedGUIPolicy):
            definitions = policy.definitions()
            report.definition_map[policy.id] = definitions.as_list()
            global_definitions.merge(definitions)

            references = policy.references()
            report.reference_map[policy.id] = references.as_list()
            global_references.merge(references)
        report.policies.add(policy)

    print("Retrieving Definitions...")
    def_factory = DefinitionDAOFactory(session)
    def_list = global_definitions.as_list()
    def_count = len(def_list)
    for count,definition_id in enumerate(def_list):
        definition = def_factory.from_type(DefinitionType(definition_id[0])).get_by_id(definition_id[1])
        print("[{count}/{total}] {defi}".format(count=count + 1,total=def_count,defi=definition))
        if not isinstance(definition,CflowdDefinition):
            references = definition.references(accumulator=CentralizedReferences())
            report.reference_map[definition.id] = references.as_list()
            global_references.merge(references)
        report.definitions.add(definition)

    print("Retrieving References...")
    ref_factory = ListDAOFactory(session)
    ref_list = global_references.as_list()
    ref_count = len(ref_list)
    for count,ref_id in enumerate(ref_list):
        listd = ref_factory.from_reference_type(ReferenceType(ref_id[0])).get_by_id(ref_id[1])
        print("[{count}/{total}] {lst}".format(count=count + 1,total=ref_count,lst=listd))
        report.references.add(listd)

    return report

def main():
    config = Configuration.from_file("./config.json")
    with vManageSession(config.server) as session:
        print("Attempting to Login...")
        if session.login(config.username,config.password):
                print("Successful Login.")
                report = extract_policies(session)
                print("Saving report...")
                with open(config.file,"wt",encoding=config.encoding) as export_file:
                    json.dump(report.to_dict(),export_file)
        else:
            print("Login Failed.")

main()