from hvicinga import HVIcinga
from hvalertmanager import HVAlertManager
from hvnetbox import HVNetbox
from hvopenstack import HVOpenstack
from hvssh import HVSSH
from hvaquilon import HVAquilon
from hvkayobe import HVKayobe
from hvjira import HVJira

import logging

class HyperVisorManager:
    def __init__(self, migration_manager, creds_handler, request, time_interval): 
        self.log = logging.getLogger(f'hypervisormanager:{request.hypervisor}')
        self.migration_manager = migration_manager
        self.creds_handler = creds_handler
        self.request = request
        self.time_interval = time_interval
        self.jira = HVJira(self)
        self.hvicinga = HVIcinga(self)
        self.hvalertmanager = HVAlertManager(self)
        self.hvnetbox = HVNetbox(self)
        self.hvopenstack = HVOpenstack(self)
        self.hvssh = HVSSH(self)
        self.hvaquilon = HVAquilon(self)
        self.hvkayobe = HVKayobe(self)

    def run(self, step):
        self.log.debug('starting run')
        if step == "setup":
            self._run_setup()
        elif step == "pre-bios":
            self._run_pre_bios()
        elif step == "post-bios":
            self._run_post_bios()
        elif step == "finish":
            self._run_finish()
        self.log.debug('leaving run')

    def _run_setup(self):
        try:
            self.log.debug('starting _run_setup')
            self.hvssh.ensure_root_access()
            self.log.debug('leaving _run_setup')
        except Exception as ex:
            msg = f"An ERROR occurred {ex}. Aborting automation for hypervisor {self.request.hypervisor}"

    def _run_pre_bios(self):
        try:
            self.log.debug('starting _run_pre_bios')
            self.jira.move_to_working_on_pre_bios()
            if not self.hvssh.is_rocky_8:
                msg = "the hypervisor {self.request.hypervisor} is not Rocky 8. Aborting"
                raise Exception(msg)
            self.hvicinga.create_downtime()
            self.hvalertmanager.create_silence()
            self.hvopenstack.disable_service()
            if self.hvnetbox.status not in ["active", "offfline"]:
                msg = "status of hypervisor {self.request.hypervisor} in Netbox is neither Active nor Offline. Aborting."
                raise Exception(msg)
            self.hvnetbox.change({"status":"planned"})
            self.hvkayobe.run_mellanox()
            self.hvaquilon.run(f"reimport-host.sh {self.request.hypervisor}")
            self.hvaquilon.run(f"remove_interfaces.py {self.request.hypervisor}")
            self.hvaquilon.run(f"prepare_host.py {self.request.hypervisor}")
            self.jira.move_to_ready_for_reinstall()
            self.log.debug('leaving _run_pre_bios')
        except Exception as ex:
            msg = f"An ERROR occurred {ex}. Aborting automation for hypervisor {self.request.hypervisor}"
            self.log.debug(msg)
            self.jira.add_comment(msg)
            self.jira.move_to_pre_bios_failed()

    def _run_post_bios(self):
        self.log.debug('starting _run_post_bios')
        self.jira.move_to_working_on_post_reinstall()
        
        blocks_info = self.hvssh.blocks_info
        self.log.debug(blocks_info)
        self.jira.add_comment("lsblk info:")
        self.jira.add_block(blocks_info)
        self.jira.add_comment()

        gpus_info = self.hvssh.gpus_info
        self.log.debug(gpus_info)
        self.jira.add_comment("lspci info:")
        self.jira.add_block(gpus_info)
        self.jira.add_comment()

        efi_msg = f"hv is UEFI? {self.hvssh.is_efi}"
        self.log.debug(efi_msg)
        self.jira.add_comment(efi_msg)

        #self.hvaquilon.run(f"aq make --hostname {self.request.hypervisor} --personality kayobe-prod")
        self.hvnetbox.change({"status":"active", "role":"Openstack Prod Kolla_Compute"})
        self.log.debug('leaving _run_post_bios')





#    def _run_finish(self):
#        self.log.debug('starting _run_finish')
#        self._finish_icinga()
#        self._finish_alertmanager()
#        self.log.debug('leaving _run_finish')
#
#
#    def _finish_icinga(self):
#        self.log.debug('starting _finish_icinga')
#        hv_icinga = HVIcinga(self.creds_handler, self.request.hypervisor)
#        hv_icinga.remove_downtime()
#        msg = "downtime removed from Icinga"
#        self.log.debug(msg)
#        self.jira.add_comment(msg)
#        self.log.debug('leaving _finish_icinga')
#
#    def _finish_alertmanager(self):
#        self.log.debug('starting _finish_alertmanager')
#        hv_alertmanager = HVAlertManager(self.creds_handler, self.request.hypervisor)
#        hv_alertmanager.remove_silence()
#        msg = "silence removed from AlertManager"
#        self.log.debug(msg)
#        self.jira.add_comment(msg)
#        self.log.debug('leaving _finish_alertmanager')

