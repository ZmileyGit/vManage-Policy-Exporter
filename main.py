from vmanage.config import Configuration

from vmanage.auth import vManageSession

from vmanage.entity import Server

from vmanage.lists.dao import DataPrefixListDAO,PolicerDAO,PrefixListDAO
from vmanage.lists.dao import ApplicationListDAO,SiteListDAO,SLAClassDAO
from vmanage.lists.dao import TLOCListDAO,VPNListDAO,ColorListDAO

from vmanage.policy.centralized.dao import PoliciesDAO,DefinitionDAOFactory
from vmanage.policy.centralized.tool import CentralizedReferences
from vmanage.policy.centralized.model import GUIPolicy,HubNSpokeDefinition
from vmanage.policy.centralized.model import MeshDefinition,ControlDefinition

def extract_policies(server,user,password):
    with vManageSession(server,secure=False) as session:
        if session.login(user,password):
            centralized_policies = PoliciesDAO(session)
            definition_dao_fac = DefinitionDAOFactory(session)
            policies = centralized_policies.get_all()
            references = CentralizedReferences()
            for policy in policies:
                if isinstance(policy,GUIPolicy):
                    assembly = policy.assembly
                    for application in assembly:
                        print("\n{klass} | {0}".format(application.type,klass=type(application).__name__))
                        definition = definition_dao_fac.from_type(application.type).get_by_id(application.id)
                        if isinstance(definition,HubNSpokeDefinition) or isinstance(definition,MeshDefinition) or isinstance(definition,ControlDefinition):
                            print(definition.definition)
                            definition.references(accumulator=references)
            print("\n---All References---")
            print(references)
            data_prefix_dao = DataPrefixListDAO(session)
            for data_prefix_ref in references.data_prefix_lists:
                data_prefix_list = data_prefix_dao.get_by_id(data_prefix_ref)
                print(data_prefix_list)
            
            policer_dao = PolicerDAO(session)
            for policer_ref in references.policers:
                policer = policer_dao.get_by_id(policer_ref)
                print(policer)

            prefix_list_dao = PrefixListDAO(session)
            for prefix_list_ref in references.prefix_lists:
                prefix_list = prefix_list_dao.get_by_id(prefix_list_ref)
                print(prefix_list)

            application_list_dao = ApplicationListDAO(session)
            for application_list_ref in references.application_lists:
                application_list = application_list_dao.get_by_id(application_list_ref)
                print(application_list)

            color_list_dao = ColorListDAO(session)
            for color_list_ref in references.color_lists:
                color_list = color_list_dao.get_by_id(color_list_ref)
                print(color_list)

            site_list_dao = SiteListDAO(session)
            for site_list_ref in references.site_lists:
                site_list = site_list_dao.get_by_id(site_list_ref)
                print(site_list)

            sla_class_dao = SLAClassDAO(session)
            for sla_class_ref in references.sla_classes:
                sla_class = sla_class_dao.get_by_id(sla_class_ref)
                print(sla_class)

            tloc_list_dao = TLOCListDAO(session)
            for tloc_list_ref in references.tloc_lists:
                tloc_list = tloc_list_dao.get_by_id(tloc_list_ref)
                print(tloc_list)

            vpn_list_dao = VPNListDAO(session)
            for vpn_list_ref in references.vpn_lists:
                vpn_list = vpn_list_dao.get_by_id(vpn_list_ref)
                print(vpn_list)

def main():
    config = Configuration.from_file("./config.json")
    extract_policies(config.server,config.username,config.password)

main()