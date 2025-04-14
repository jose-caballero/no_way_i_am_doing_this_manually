from hvicinga import HVIcinga
from hvalertmanager import HVAlertManager
from hvnetbox import HVNetbox
from hvopenstack import HVOpenstack
from hvssh import HVSSH
from hvaquilon import HVAquilon
from hvkayobe import HVKayobe
from hvjira import HVJira, HVJiraMessage

import logging

class HyperVisorManager:
    def __init__(self, creds_handler, request, time_interval): 
        self.log = logging.getLogger(f'hypervisormanager:{request.hypervisor}')
        self.creds_handler = creds_handler
        self.request = request
        self.time_interval = time_interval
        self.hvjira = HVJira(self)
        self.hvicinga = HVIcinga(self)
        self.hvalertmanager = HVAlertManager(self)
        self.hvnetbox = HVNetbox(self)
        self.hvopenstack = HVOpenstack(self)
        self.hvssh = HVSSH(self)
        self.hvaquilon = HVAquilon(self)
        self.hvkayobe = HVKayobe(self)

    def run(self, step):
        self.log.debug('starting run')
        if step == "pre-bios":
            self._run_pre_bios()
        elif step == "post-bios":
            self._run_post_bios()
        elif step == "finish":
            self._run_finish()
        self.log.debug('leaving run')

    def _run_pre_bios(self):
        self.log.debug('starting _run_pre_bios')
        self.jira.move_to_working_on_pre_bios()
        try:
            self._pre_bios_icinga()
            self._pre_bios_alertmanager()
            self._pre_bios_openstack()
            self._pre_bios_netbox()
            self._pre_bios_mellanox()
            self._pre_bios_aquilon()
        except Exception as ex:
            msg = f"An ERROR occurred {ex}. Aborting automation for hypervisor {self.request.hypervisor}"
            self.log.debug(msg)
            self.jira.add_comment(msg)
            self.jira.move_to_blocked()
        self.log.debug('leaving _run_pre_bios')

    def _run_post_bios(self):
        self.log.debug('starting _run_post_bios')
        try:
            self._post_bios_aquilon()
            self._post_bios_netbox()
        except Exception as ex:
            pass
        self.log.debug('leaving _run_post_bios')

    def _run_finish(self):
        self.log.debug('starting _run_finish')
        try:
            self._finish_icinga()
            self._finish_alertmanager()
        except Exception as ex:
            pass
        self.log.debug('leaving _run_finish')


    def _pre_bios_icinga(self):
        self.log.debug('starting _pre_bios_icinga')
        hv_icinga = HVIcinga(self.creds_handler, self.request.hypervisor, self.time_interval)
        if hv_icinga.host_is_registered:
            response = hv_icinga.create_downtime()
            if response.ok:
                downtime_name = response.json()['results'][0]['name']
                msg = f"downtime in Icinga created successfully, from {self.time_interval.start_str} to {self.time_interval.end_str}. Downtime name: {downtime_name}"
                self.log.debug(msg)
                self.jira.add_comment(msg)
            else:
                msg = f"creating downtime from {self.time_interval.start_str} to {self.time_interval.end_str} failed: {response.text}"
                self.log.debug(msg)
                self.jira.add_comment(msg)
        else:
            msg = "Hypervisor is not registered in Icinga, no need for downtime."
            self.log.debug(msg)
            self.jira.add_comment(msg)
        self.log.debug('leaving _pre_bios_icinga')

    def _pre_bios_alertmanager(self):
        self.log.debug('starting _pre_bios_alertmanager')
        hv_alertmanager = HVAlertManager(self.creds_handler, self.request.hypervisor, self.time_interval)
        out_msg = hv_alertmanager.create_silence()
        msg = f"silence created in AlertManager successfully, from {self.time_interval.start_str} to {self.time_interval.end_str}"
        msg += "\n"
        msg += out_msg
        self.log.debug(msg)
        self.jira.add_comment(msg)
        self.log.debug('leaving _pre_bios_alertmanager')

    def _pre_bios_openstack(self):
        self.log.debug('starting _pre_bios_openstack')
        hv_openstack = HVOpenstack(self.creds_handler, self.request.hypervisor, self.time_interval)
        if hv_openstack.is_enabled:
            hv_openstack.disable_service()
            msg = "hypervisor disabled from OpenStack"
            self.log.debug(msg)
            self.jira.add_comment(msg)
        else:
            msg = "the hypervisor was already disabled from OpenStack. Nothing to do"
            self.log.debug(msg)
            self.jira.add_comment(msg)
        self.log.debug('leaving _pre_bios_openstack')

    def _pre_bios_netbox(self):
        self.log.debug('starting _pre_bios_netbox')
        hv_netbox = HVNetbox(self.creds_handler, self.request.hypervisor)
        hv_netbox.change_status("planned")
        msg = "status changed in NetBox to value Planned"
        msg += "\n"
        msg += hv_netbox.url
        self.log.debug(msg)
        self.jira.add_comment(msg)
        self.log.debug('leaving _pre_bios_netbox')

    def _pre_bios_mellanox(self):
        self.log.debug('starting _pre_bios_mellanox')
        ssh_hypervisor = HVSSH(self.creds_handler, self.request.hypervisor)
        out, err, rc = ssh_hypervisor.run("lspci | grep -i mellanox")
        if out != "":
            jiramsg = HVJiraMessage()
            msg = "Mellanox card found on the hypervisor"
            jiramsg.add(msg)
            msg += "\n"
            msg += out
            self.log.debug(msg)
            jiramsg.add_block(out)
            ssh_kayobe = HVKayobe(self.creds_handler, self.request.hypervisor)
            out_kayobe, err_kayobe, rc_kayobe = ssh_kayobe.run_mellanox()
            if rc_kayobe == 0:
                msg = "ansible playbook mellanox-enable-uefi-pxe.yml executed for the hypervisor"
            else:
                msg = "ansible playbook mellanox-enable-uefi-pxe.yml failed for the hypervisor"
            self.log.debug(msg)
            jiramsg.add(msg)
            jiramsg.add_block(out_kayobe)
            self.jira.add_comment(jiramsg)
            if rc_kayobe != 0:
                raise Exception(msg)
        else:
            msg = "no Mellanox card found on the hypervisor, nothing to do"
            self.log.debug(msg)
            self.jira.add_comment(msg)
        self.log.debug('leaving _pre_bios_mellanox')

    def _pre_bios_aquilon(self):
        self.log.debug('starting _pre_bios_aquilon')
        aq = HVAquilon(self.creds_handler)
        aq.run(f"remove-host.sh {self.request.hypervisor}")
        msg = "remote_host script executed on the Aquilon host"
        self.log.debug(msg)
        self.jira.add_comment(msg)
        aq.run(f"aq make --hostname {self.request.hypervisor} --personality inventory --archetype cloud --osname rocky --osversion 9x-x86_64")
        msg = "hypervisor recompiled on the Aquilon host with Personality inventory"
        self.log.debug(msg)
        self.jira.add_comment(msg)
        aq.run(f"aq pxeswitch --hostname {self.request.hypervisor} --install")
        msg = "hypervisor pxeswitched on the Aquilon host"
        self.log.debug(msg)
        self.jira.add_comment(msg)
        self.log.debug('leaving _pre_bios_aquilon')


    def _post_bios_aquilon(self):
        self.log.debug('starting _post_bios_aquilon')
        aq = HVAquilon(self.creds_handler)
        aq.run(f"aq make --hostname {self.request.hypervisor} --personality kayobe-prod")
        msg = "hypervisor recompiled on the Aquilon host with Personality kayobe-prod"
        self.log.debug(msg)
        self.jira.add_comment(msg)
        self.log.debug('leaving _post_bios_aquilon')

    def _post_bios_netbox(self):
        self.log.debug('starting _post_bios_netbox')
        hv_netbox = HVNetbox(self.creds_handler, self.request.hypervisor)
        hv_netbox.change_status("staged")
        msg = "status changed in NetBox to value Staged"
        self.log.debug(msg)
        self.jira.add_comment(msg)
        hv_netbox.change_role("Openstack Prod Kolla_Compute")
        msg = "role changed in NetBox to value Openstack Prod Kolla_Compute"
        self.log.debug(msg)
        self.jira.add_comment(msg)
        self.log.debug('leaving _post_bios_netbox')

    def _finish_icinga(self):
        self.log.debug('starting _finish_icinga')
        hv_icinga = HVIcinga(self.creds_handler, self.request.hypervisor)
        hv_icinga.remove_downtime()
        msg = "downtime removed from Icinga"
        self.log.debug(msg)
        self.jira.add_comment(msg)
        self.log.debug('leaving _finish_icinga')

    def _finish_alertmanager(self):
        self.log.debug('starting _finish_alertmanager')
        hv_alertmanager = HVAlertManager(self.creds_handler, self.request.hypervisor)
        hv_alertmanager.remove_silence()
        msg = "silence removed from AlertManager"
        self.log.debug(msg)
        self.jira.add_comment(msg)
        self.log.debug('leaving _finish_alertmanager')

