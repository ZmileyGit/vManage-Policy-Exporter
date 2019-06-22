from vmanage.config import Configuration
from vmanage.auth import vManageSession

from vmanage.scripts.tool import PolicyExportFormat

from vmanage.policy.localized.model import LocalizedGUIPolicy
from vmanage.policy.localized.dao import PoliciesDAO
from vmanage.policy.localized.tool import LocalizedDefinitions,LocalizedReferences

def main():
    config = Configuration.from_file("./config.json")
    with vManageSession(config.server) as session:
        if session.login(config.username,config.password):
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
                report.definitions.add(policy)
            
            print("Retrieving Definitions...")
main()