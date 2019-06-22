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
    for policy in policies:
        if isinstance(policy,LocalizedGUIPolicy):
            definitions = policy.definitions()
            report.definition_map[policy.id] = definitions.as_list()
            global_definitions.merge(definitions)
        report.policies.add(policy)
    
    print("Retrieving Definitions...")
    def_factory = DefinitionDAOFactory(session)
    for definition_id in global_definitions.as_list():
        definition = def_factory.from_type(DefinitionType(definition_id[0])).get_by_id(definition_id[1])
        if not isinstance(definition,QoSMapDefinition):
            definition.references(accumulator=global_references)
        report.definitions.add(definition)

    print("Retrieving References...")
    ref_factory = ListDAOFactory(session)
    for ref_id in global_references.as_list():
        listd = ref_factory.from_reference_type(ReferenceType(ref_id[0])).get_by_id(ref_id[1])
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