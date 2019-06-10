import json
import re

from vmanage.entity import Server
from vmanage.config import Configuration
from vmanage.auth import vManageSession
from vmanage.error import CodedAPIError

from vmanage.scripts.tool import PolicyExportFormat,PolicyImportReport,map_sub
from vmanage.lists.dao import ListDAOFactory

from vmanage.policy.centralized.model import DefinitionFactory,PolicyFactory
from vmanage.policy.centralized.dao import DefinitionDAOFactory,PolicyDAOFactory
from vmanage.policy.centralized.dao import PoliciesDAO

def insert_policies(report:PolicyExportFormat,server:Server,username:str,password:str,rollback=False):
    with vManageSession(server) as session:
        if session.login(username,password):
            imports = PolicyImportReport()
            originals = report.to_dict()
            list_dao_fac = ListDAOFactory(session)
            for reference in report.references:
                ref_dao = list_dao_fac.from_type(reference.type)
                old_id = reference.id
                print("Creating List...")
                ref_dao.force_create(reference)
                imports.references.add(reference)
                imports.reference_map[old_id] = reference.id
                print(reference)


            definitions_str = json.JSONEncoder().encode(originals[PolicyExportFormat.DEFINITIONS_FIELD])
            list_regex = re.compile("({0})".format("|".join(imports.reference_map.keys())))
            new_definitions_str = re.sub(list_regex,map_sub(imports.reference_map),definitions_str)
            new_definitions_json = json.JSONDecoder().decode(new_definitions_str)
            def_fac = DefinitionFactory()
            imports.definitions.update(def_fac.from_dict(document) for document in new_definitions_json)

            def_dao_fac = DefinitionDAOFactory(session)
            for definition in imports.definitions:
                def_dao = def_dao_fac.from_type(definition.type)
                old_id = definition.id
                print("Creating Definition...")
                def_dao.force_create(definition)
                imports.definition_map[old_id] = definition.id
                print(definition)

            policies_str = json.JSONEncoder().encode(originals[PolicyExportFormat.POLICIES_FIELD])
            new_policies_str = re.sub(list_regex,map_sub(imports.reference_map),policies_str)
            def_regex = "({0})".format("|".join(imports.definition_map.keys()))
            new_policies_str = re.sub(def_regex,map_sub(imports.definition_map),new_policies_str)
            new_policies_json = json.JSONDecoder().decode(new_policies_str)
            policy_fac = PolicyFactory()
            imports.policies.update(policy_fac.from_dict(document) for document in new_policies_json)

            policy_dao_fac = PolicyDAOFactory(session)
            for policy in imports.policies:
                policy_dao = policy_dao_fac.from_type(policy.type)
                old_id = policy.id
                print("Creating Policy...")
                policy_dao.force_create(policy)
                print(policy)

            policies_dao = PoliciesDAO(session)
            name_id_map = {}
            for policy in policies_dao.get_all():
                name_id_map[policy.name] = policy.id

            for policy in imports.policies:
                policy.id = name_id_map[policy.name]
                print(policy)

            if rollback:
                for policy in imports.policies:
                    policy_dao = policy_dao_fac.from_type(policy.type)
                    print("Deleting policy...")
                    print(policy_dao.delete(policy.id))

                for definition in imports.definitions:
                    def_dao = def_dao_fac.from_type(definition.type)
                    print("Deleting Definition...")
                    print(def_dao.delete(definition.id))

                for reference in imports.references:
                    ref_dao = list_dao_fac.from_type(reference.type)
                    print("Deleting List '{0}'...".format(reference.id))
                    print(ref_dao.delete(reference.id))
                
            return imports
    return None

def main():
    config = Configuration.from_file("./config.json")
    with open(config.file,"rt",encoding=config.encoding) as raw_report:
        json_report = json.load(raw_report)
        report = PolicyExportFormat.from_dict(json_report)
        insert_policies(report,config.server,config.username,config.password)

main()