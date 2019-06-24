import json

from vmanage.config import Configuration
from vmanage.auth import vManageSession

from vmanage.lists.dao import ListDAOFactory

from vmanage.scripts.tool import PolicyExportFormat

from vmanage.policy.tool import DefinitionType,ReferenceType

from vmanage.policy.localized.model import LocalizedGUIPolicy,QoSMapDefinition
from vmanage.policy.localized.dao import PoliciesDAO,DefinitionDAOFactory
from vmanage.policy.localized.tool import LocalizedDefinitions,LocalizedReferences

def extract_localized_policies(session:vManageSession):
    policies_dao = PoliciesDAO(session)
    policies = policies_dao.get_all()
    global_definitions = LocalizedDefinitions()
    global_references = LocalizedReferences()
    report = PolicyExportFormat()

    policy_count = len(policies)
    print("Retrieving Localized Polices...")
    for count,policy in enumerate(policies):
        print("[{count}/{total}] {policy}".format(count=count + 1,total=policy_count,policy=policy))
        if isinstance(policy,LocalizedGUIPolicy):
            definitions = policy.definitions()
            report.definition_map[policy.id] = definitions.as_list()
            global_definitions.merge(definitions)
        report.policies.add(policy)
    
    print("Retrieving Definitions...")
    def_factory = DefinitionDAOFactory(session)
    def_list = global_definitions.as_list()
    def_count = len(def_list)
    for count,definition_id in enumerate(def_list):
        definition = def_factory.from_type(DefinitionType(definition_id[0])).get_by_id(definition_id[1])
        print("[{count}/{total}] {defi}".format(count=count + 1,total=def_count,defi=definition))
        if not isinstance(definition,QoSMapDefinition):
            references = definition.references(accumulator=LocalizedReferences())
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
                report = extract_localized_policies(session)
                print("Saving report...")
                with open(config.file,"wt",encoding=config.encoding) as export_file:
                    json.dump(report.to_dict(),export_file)
        else:
            print("Login Failed.")
               
main()