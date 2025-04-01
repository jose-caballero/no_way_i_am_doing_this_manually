from hvicinga import HVIcinga
from hvalertmanager import HVAlertManager
from hvnetbox import HVNetbox
from hvopenstack import HVOpenstack
from hvssh import HVSSH
from hvaquilon import HVAquilon

class HyperVisorManager:
    def __init__(self, creds_handler, request, time_interval, jira): 
        self.creds_handler = creds_handler
        self.request = request
        self.time_interval = time_interval
        self.jira = jira

    def run(self, step):
        if step == "pre-bios":
            self._run_pre_bios()
        elif step == "post-bios":
            self._run_post_bios()
        elif step == "finish":
            self._run_finish()
        else:
            print("huh!?")

    def _run_pre_bios(self):

        hv_icinga = HVIcinga(self.creds_handler, self.request.hypervisor, self.time_interval)
        if hv_icinga.host_is_registered:
            hv_icinga.create_downtime()
            self.jira.add_comment(self.request.jira_issue_key, f"downtime in Icinga created successfully, from {self.time_interval.start_str} to {self.time_interval.end_str}")
        else:
            self.jira.add_comment(self.request.jira_issue_key, "Hypervisor is not registered in Icinga, no need for downtine.")

        hv_alertmanager = HVAlertManager(self.creds_handler, self.request.hypervisor, self.time_interval)
        hv_alertmanager.create_silence()
        self.jira.add_comment(self.request.jira_issue_key, f"silence created in AlertManager successfully, from {self.time_interval.start_str} to {self.time_interval.end_str}")
        
        hv_openstack = HVOpenstack(self.creds_handler, self.request.hypervisor, self.time_interval)
        hv_openstack.disable_service()
        self.jira.add_comment(self.request.jira_issue_key, "hypervisor disabled from OpenStack")

        hv_netbox = HVNetbox(self.creds_handler, self.request.hypervisor)
        hv_netbox.change_status("planned")
        self.jira.add_comment(self.request.jira_issue_key, "status changed in NetBox to value Planned")

        ssh_hypervisor = HVSSH(self.creds_handler, self.request.hypervisor)
        out, err, rc = ssh_hypervisor.run("lspci | grep -i mellanox")
        if out != "":
            self.jira.add_comment(self.request.jira_issue_key, "Mellanox card found on the hypervisor")
            ssh_kayobe = HVSSH(self.creds_handler, "hv815.nubes.rl.ac.uk")
            kayobe_cmd = f'source ./kayobe-prod/production-env-vars.sh; ansible-playbook ansible/mellanox-enable-uefi-pxe.yml -i {self.request.hypervisor}, --extra-vars "pxe_target={self.hostname}'
            ssh_kayobe.run(kayobe_cmd)
            self.jira.add_comment(self.request.jira_issue_key, "ansible playbook mellanox-enable-uefi-pxe.yml executed for the hypervisor")
        else:
            self.jira.add_comment(self.request.jira_issue_key, "no Mellanox card found on the hypervisor")

        aq = HVAquilon(self.creds_handler)
        aq.run(f"remove_host.sh {self.request.hypervisor}")
        self.jira.add_comment(self.request.jira_issue_key, "remote_host script executed on the Aquilon host")
        aq.run(f"aq make --hostname {self.request.hypervisor} --personality inventory --archetype cloud --osname rocky --osversion 9x-x86_64")
        self.jira.add_comment(self.request.jira_issue_key, "hypervisor recompiled on the Aquilon host with Personality inventory")
        aq.run(f"aq pxeswitch --hostname {self.request.hypervisor} --install")
        self.jira.add_comment(self.request.jira_issue_key, "hypervisor pxeswitched on the Aquilon host")


    def _run_post_bios(self):

        aq = HVAquilon(self.creds_handler)
        aq.run(f"aq make --hostname {self.request.hypervisor} --personality kayobe-prod")
        self.jira.add_comment(self.request.jira_issue_key, "hypervisor recompiled on the Aquilon host with Personality kayobe-prod")

        hv_netbox = HVNetbox(self.creds_handler, self.request.hypervisor)
        hv_netbox.change_status("staged")
        self.jira.add_comment(self.request.jira_issue_key, "status changed in NetBox to value Staged")
        hv_netbox.change_role("Openstack Prod Kolla_Compute")
        self.jira.add_comment(self.request.jira_issue_key, "role changed in NetBox to value Openstack Prod Kolla_Compute")


    def _run_finish(self):
        
        hv_icinga = HVIcinga(self.creds_handler, self.request.hypervisor)
        hv_icinga.remove_downtime()
        self.jira.add_comment(self.request.jira_issue_key, "downtime removed from Icinga")

        hv_alertmanager = HVAlertManager(self.creds_handler, self.request.hypervisor)
        hv_alertmanager.remove_silence()
        self.jira.add_comment(self.request.jira_issue_key, "silence removed from AlertManager")
