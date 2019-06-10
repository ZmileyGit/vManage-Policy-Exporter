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
from vmanage.policy.centralized.model import GUIPolicy

def extract_policies(server,user,password):
    with vManageSession(server) as session:
        print("Attempting to Login...")
        if session.login(user,password):
            print("Successful Login")
            centralized_policies = PoliciesDAO(session)
            print("Retrieving Centralized Polices...")
            policies = centralized_policies.get_all()
            global_definitions = CentralizedDefinitions()
            global_references = CentralizedReferences()
            report = PolicyExportFormat()
            for policy in policies:
                if isinstance(policy,GUIPolicy):
                    definitions = policy.definitions()
                    report.definition_map[policy.id] = definitions.as_list()
                    global_definitions.merge(definitions)

                    references = policy.references()
                    report.reference_map[policy.id] = references.as_list()
                    global_references.merge(references)
                report.policies.add(policy)

            print("Retrieving Definitions...")
            def_factory = DefinitionDAOFactory(session)
            for definition_id in global_definitions.as_list():
                definition = def_factory.from_type(DefinitionType(definition_id[0])).get_by_id(definition_id[1])
                if not isinstance(definition,CflowdDefinition):
                    definition.references(accumulator=global_references)
                report.definitions.add(definition)

            print("Retrieving References...")
            ref_factory = ListDAOFactory(session)
            for ref_id in global_references.as_list():
                listd = ref_factory.from_reference_type(ReferenceType(ref_id[0])).get_by_id(ref_id[1])
                report.references.add(listd)

            return report
    return None

def main():
    config = Configuration.from_file("./config.json")
    report = extract_policies(config.server,config.username,config.password)
    if report:
        print("Saving report...")
        with open(config.file,"wt",encoding=config.encoding) as export_file:
            json.dump(report.to_dict(),export_file)

main()