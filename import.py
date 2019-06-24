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

def insert_policies(report:PolicyExportFormat,session:vManageSession,rollback=False):
    imports = PolicyImportReport()
    originals = report.to_dict()
    list_dao_fac = ListDAOFactory(session)

    print("Creating References...")
    ref_count = len(report.references)
    ref_error = False
    for count,reference in enumerate(report.references):
        ref_dao = list_dao_fac.from_type(reference.type)
        old_id = reference.id
        try:
            ref_dao.force_create(reference)
        except CodedAPIError as error:
            ref_error = True
            print("{0}({1}): {2}".format(error.error.code,error.error.message,error.error.details))
        else:
            imports.references.add(reference)
            imports.reference_map[old_id] = reference.id
        finally:
            print("[{count}/{total}] {reference}".format(count=count + 1,total=ref_count,reference=reference))

    if not ref_error:
        definitions_str = json.JSONEncoder().encode(originals[PolicyExportFormat.DEFINITIONS_FIELD])
        list_regex = re.compile("({0})".format("|".join(imports.reference_map.keys())))
        new_definitions_str = re.sub(list_regex,map_sub(imports.reference_map),definitions_str)
        new_definitions_json = json.JSONDecoder().decode(new_definitions_str)
        def_fac = DefinitionFactory()
        imports.definitions.update(def_fac.from_dict(document) for document in new_definitions_json)

        def_dao_fac = DefinitionDAOFactory(session)
        print("Creating Definitions...")
        def_count = len(imports.definitions)
        def_error = False
        for count,definition in enumerate(imports.definitions):
            def_dao = def_dao_fac.from_type(definition.type)
            old_id = definition.id
            try:
                def_dao.force_create(definition)
            except CodedAPIError as error:
                def_error = True
                print("{0}({1}): {2}".format(error.error.code,error.error.message,error.error.details))
            else:
                imports.definition_map[old_id] = definition.id
            finally:
                print("[{count}/{total}] {defi}".format(count=count + 1,total=def_count,defi=definition))

        if not def_error:
            policies_str = json.JSONEncoder().encode(originals[PolicyExportFormat.POLICIES_FIELD])
            new_policies_str = re.sub(list_regex,map_sub(imports.reference_map),policies_str)
            def_regex = "({0})".format("|".join(imports.definition_map.keys()))
            new_policies_str = re.sub(def_regex,map_sub(imports.definition_map),new_policies_str)
            new_policies_json = json.JSONDecoder().decode(new_policies_str)
            policy_fac = PolicyFactory()
            imports.policies.update(policy_fac.from_dict(document) for document in new_policies_json)

            print("Creating Policies...")
            policy_dao_fac = PolicyDAOFactory(session)
            poli_count = len(imports.policies)
            poli_error = False
            for count,policy in enumerate(imports.policies):
                policy_dao = policy_dao_fac.from_type(policy.type)
                old_id = policy.id
                try:
                    policy_dao.force_create(policy)
                except CodedAPIError as error:
                    poli_error = True
                    print("{0}({1}): {2}".format(error.error.code,error.error.message,error.error.details))
                finally:
                    print("[{count}/{total}] {poli}".format(count=count + 1,total=poli_count,poli=policy))

            if not poli_error:
                policies_dao = PoliciesDAO(session)
                name_id_map = {}
                for policy in policies_dao.get_all():
                    name_id_map[policy.name] = policy.id

                for policy in imports.policies:
                    policy.id = name_id_map[policy.name]
                    print(policy)

    rollback = rollback or ref_error or def_error or poli_error
    if rollback:
        print("Deleting policies...")
        poli_count = len(imports.policies)
        for count,policy in enumerate(imports.policies):
            policy_dao = policy_dao_fac.from_type(policy.type)
            print("[{count}/{total}] {reference}".format(count=count + 1,total=ref_count,reference=reference))
            if policy.id:  
                print(policy_dao.delete(policy.id))

        print("Deleting definitions...")
        def_count = len(imports.definitions)
        for count,definition in enumerate(imports.definitions):
            def_dao = def_dao_fac.from_type(definition.type)
            print("[{count}/{total}] {defi}".format(count=count + 1,total=def_count,defi=definition))
            if definition.id:
                print(def_dao.delete(definition.id))

        print("Deleting lists...")
        ref_count = len(imports.references)
        for count,reference in enumerate(imports.references):
            ref_dao = list_dao_fac.from_type(reference.type)
            print("[{count}/{total}] {reference}".format(count=count + 1,total=ref_count,reference=reference))
            if reference.id:
                print(ref_dao.delete(reference.id))
        
    return imports

def main():
    config = Configuration.from_file("./config.json")
    with vManageSession(config.server) as session, open(config.file,"rt",encoding=config.encoding) as raw_report:
        json_report = json.load(raw_report)
        report = PolicyExportFormat.from_dict(json_report,PolicyFactory(),DefinitionFactory())
        print("Attempting to Login...")
        if session.login(config.username,config.password):
                print("Successful Login.")
                report = insert_policies(report,session)
        else:
            print("Login Failed.")

main()