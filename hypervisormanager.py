from hvicinga import HVIcinga
from hvalertmanager import HVAlertManager
from hvnetbox import HVNetbox
from hvopenstack import HVOpenstack
from hvssh import HVSSH
from hvaquilon import HVAquilon
from hvkayobe import HVKayobe

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
        self.jira.move_to_in_progress(self.request.jira_issue_key)
        try:
            self._pre_bios_icinga()
            self._pre_bios_alertmanager()
            self._pre_bios_openstack()
            self._pre_bios_netbox()
            self._pre_bios_mellanox()
            self._pre_bios_aquilon()
        except Exception as ex:
            msg = f"An ERROR occurred {ex}. Aborting automation for hypervsor {self.request.hypervsor}"
            print(msg)
            self.jira.add_comment(self.request.jira_issue_key, msg)
            self.jira.move_to_blocked(self.request.jira_issue_key)

    def _run_post_bios(self):
        try:
            self._post_bios_aquilon()
            self._post_bios_netbox()
        except Exception as ex:
            pass

    def _run_finish(self):
        try:
            self._finish_icinga()
            self._finish_alertmanager()
        except Exception as ex:
            pass


    def _pre_bios_icinga(self):
        try:
            hv_icinga = HVIcinga(self.creds_handler, self.request.hypervisor, self.time_interval)
            if hv_icinga.host_is_registered:
                response = hv_icinga.create_downtime()
                if response.ok:
                    downtime_name = response['results'][0]['name']
                    self.jira.add_comment(self.request.jira_issue_key, f"downtime in Icinga created successfully, from {self.time_interval.start_str} to {self.time_interval.end_str}. Downtime name: {downtime_name}")
                else:
                    self.jira.add_comment(self.request.jira_issue_key, f"creating downtime from {self.time_interval.start_str} to {self.time_interval.end_str} failed: {response.text}")
            else:
                self.jira.add_comment(self.request.jira_issue_key, "Hypervisor is not registered in Icinga, no need for downtime.")
        except Exception as ex:
            raise ex

    def _pre_bios_alertmanager(self):
        try:
            hv_alertmanager = HVAlertManager(self.creds_handler, self.request.hypervisor, self.time_interval)
            hv_alertmanager.create_silence()
            self.jira.add_comment(self.request.jira_issue_key, f"silence created in AlertManager successfully, from {self.time_interval.start_str} to {self.time_interval.end_str}")
        except Exception as ex:
            raise ex

    def _pre_bios_openstack(self):
        try:
            hv_openstack = HVOpenstack(self.creds_handler, self.request.hypervisor, self.time_interval)
            hv_openstack.disable_service()
            self.jira.add_comment(self.request.jira_issue_key, "hypervisor disabled from OpenStack")
        except Exception as ex:
            raise ex

    def _pre_bios_netbox(self):
        try:
            hv_netbox = HVNetbox(self.creds_handler, self.request.hypervisor)
            hv_netbox.change_status("planned")
            self.jira.add_comment(self.request.jira_issue_key, "status changed in NetBox to value Planned")
        except Exception as ex:
            raise ex

    def _pre_bios_mellanox(self):
        try:
            ssh_hypervisor = HVSSH(self.creds_handler, self.request.hypervisor)
            #out, err, rc = ssh_hypervisor.run("lspci | grep -i mellanox", "root")
            out, err, rc = ssh_hypervisor.run("lspci | grep -i mellanox")
            if out != "":
                self.jira.add_comment(self.request.jira_issue_key, "Mellanox card found on the hypervisor")
                ssh_kayobe = HVKayobe(self.creds_handler)
                kayobe_cmd = (
                    f"source {self.creds_handler.kayobe.prod_env_var}; "
                    f'ansible-playbook ansible/mellanox-enable-uefi-pxe.yml -i {self.request.hypervisor}, --extra-vars "pxe_target={self.request.hypervisor}"'
                )
                ssh_kayobe.run(kayobe_cmd)
                self.jira.add_comment(self.request.jira_issue_key, "ansible playbook mellanox-enable-uefi-pxe.yml executed for the hypervisor")
            else:
                self.jira.add_comment(self.request.jira_issue_key, "no Mellanox card found on the hypervisor")
        except Exception as ex:
            raise ex

    def _pre_bios_aquilon(self):
        try:
            aq = HVAquilon(self.creds_handler)
            aq.run(f"remove-host.sh {self.request.hypervisor}")
            self.jira.add_comment(self.request.jira_issue_key, "remote_host script executed on the Aquilon host")
            aq.run(f"aq make --hostname {self.request.hypervisor} --personality inventory --archetype cloud --osname rocky --osversion 9x-x86_64")
            self.jira.add_comment(self.request.jira_issue_key, "hypervisor recompiled on the Aquilon host with Personality inventory")
            aq.run(f"aq pxeswitch --hostname {self.request.hypervisor} --install")
            self.jira.add_comment(self.request.jira_issue_key, "hypervisor pxeswitched on the Aquilon host")
        except Exception as ex:
            raise ex


    def _post_bios_aquilon(self):
        try:
            aq = HVAquilon(self.creds_handler)
            aq.run(f"aq make --hostname {self.request.hypervisor} --personality kayobe-prod")
            self.jira.add_comment(self.request.jira_issue_key, "hypervisor recompiled on the Aquilon host with Personality kayobe-prod")
        except Exception as ex:
            raise ex

    def _post_bios_netbox(self):
        try:
            hv_netbox = HVNetbox(self.creds_handler, self.request.hypervisor)
            hv_netbox.change_status("staged")
            self.jira.add_comment(self.request.jira_issue_key, "status changed in NetBox to value Staged")
            hv_netbox.change_role("Openstack Prod Kolla_Compute")
            self.jira.add_comment(self.request.jira_issue_key, "role changed in NetBox to value Openstack Prod Kolla_Compute")
        except Exception as ex:
            raise ex

    def _finish_icinga(self):
        try:
            hv_icinga = HVIcinga(self.creds_handler, self.request.hypervisor)
            hv_icinga.remove_downtime()
            self.jira.add_comment(self.request.jira_issue_key, "downtime removed from Icinga")
        except Exception as ex:
            raise ex

    def _finish_alertmanager(self):
        try:
            hv_alertmanager = HVAlertManager(self.creds_handler, self.request.hypervisor)
            hv_alertmanager.remove_silence()
            self.jira.add_comment(self.request.jira_issue_key, "silence removed from AlertManager")
        except Exception as ex:
            raise ex

