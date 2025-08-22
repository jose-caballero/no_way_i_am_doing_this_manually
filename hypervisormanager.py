from hvalertmanager import HVAlertManager
from hvnetbox import HVNetbox
from hvopenstack import HVOpenstack
from hvssh import HVSSH
from hvaquilon import HVAquilon
from hvkayobe import HVKayobe
from hvjira import HVJira
from hvexception import HVException

class HyperVisorManager:
    def __init__(self, migration_manager, creds_handler, request, time_interval):
        """
        High level orchestration for HyperVisor migration steps
        Coordinate the various services used to migrate a HyperVisor
        Initialise and create helpers for the target HyperVisor
        """
        self.migration_manager = migration_manager
        self.creds_handler = creds_handler
        self.request = request
        self.time_interval = time_interval
        self.jira = HVJira(self)
        self.hvalertmanager = HVAlertManager(self)
        self.hvnetbox = HVNetbox(self)
        self.hvopenstack = HVOpenstack(self)
        self.hvaquilon = HVAquilon(self)
        self.hvssh = HVSSH(self)
        self.hvkayobe = HVKayobe(self)

    def run(self, step):
        """
        Dispatch execution to the appropriate step handler
        """
        if step == "setup":
            self._run_setup()
        elif step == "pre-drain":
            self._run_pre_drain()
        elif step == "drain":
            self._run_drain()
        elif step == "pre-reinstall":
            self._run_pre_reinstall()
        elif step == "post-reinstall":
            self._run_post_reinstall()
        elif step == "adoption":
            self._run_adoption()
        elif step == "noops":
            self._run_noops()

    def _run_setup(self):
        try:
            self.hvssh.ensure_root_access()
        except HVException as ex:
            msg = f"An ERROR occurred {ex}. Aborting automation for hypervisor {self.request.hypervisor}"
            print(msg)

    def _run_pre_drain(self):
        try:
            self.hvssh.is_rocky_8()
            self.hvssh.update_qemu_kvm()
            self.hvnetbox.hv_in_netbox()
            self.hvnetbox.check_status_pre_drain()
        except HVException as ex:
            msg = f"An ERROR occurred {ex}. Aborting automation for hypervisor {self.request.hypervisor}"
            print(msg)
            self.jira.add(msg)
            self.jira.send_buffer()
            self.jira.move_to_pre_reinstall_failed()

    def _run_drain(self):
        try:
            self.hvopenstack.disable_hv()
            self.hvopenstack.show_hv()
            self.hvopenstack.migrate_servers()
        except HVException as ex:
            msg = f"An ERROR occurred {ex}. Aborting automation for hypervisor {self.request.hypervisor}"
            print(msg)
            self.jira.add(msg)
            self.jira.send_buffer()
            self.jira.move_to_pre_reinstall_failed()

    def _run_pre_reinstall(self):
        try:
            self.jira.move_to_working_on_pre_bios()
            self.hvopenstack.ensure_hv_has_no_servers()
            self.hvssh.is_empty()
            self.hvssh.blocks_info()
            self.hvssh.gpus_info()
            self.hvalertmanager.create_silence()
            self.hvnetbox.change({"status":"planned"})
            if self.hvssh.mellanox_info() != "":
                self.hvkayobe.run_mellanox_playbook()
            self.hvaquilon.remove_interfaces()
            self.hvaquilon.reimport()
            self.hvaquilon.manage_to_sandbox()
            self.hvaquilon.prepare_host()
            self.jira.move_to_ready_for_reinstall()
        except HVException as ex:
            msg = f"An ERROR occurred {ex}. Aborting automation for hypervisor {self.request.hypervisor}"
            print(msg)
            self.jira.add(msg)
            self.jira.send_buffer()
            self.jira.move_to_pre_bios_failed()

    def _run_post_reinstall(self):
        try:
            self.jira.move_to_working_on_post_reinstall()
            self.hvssh.is_rocky_9()
            self.hvssh.blocks_info()
            self.hvssh.gpus_info()
            self.hvssh.verify_is_efi()
            #self.hvssh.hardware_specific()
            self.hvnetbox.change({"status":"active", "role":"Openstack Prod Kolla_Compute"})
            self.jira.move_to_ready_for_adoption()
        except HVException as ex:
            msg = f"An ERROR occurred {ex}. Aborting automation for hypervisor {self.request.hypervisor}"
            print(msg)
            self.jira.add(msg)
            self.jira.send_buffer()


    def _run_adoption(self):
        try:
            #self.jira.move_to_working_on_adoption()
            #self.hvkayobe.run_inventory_from_netbox()
            #self.hvkayobe.run_kayobe_overcloud_host_configure()
            #self.hvkayobe.run_kayobe_overcloud_deploy_hypervisor()
            #self.hvkayobe.run_kayobe_overcloud_deploy_controller()

            self.hvopenstack.enable_hv()

        except HVException as ex:
            msg = f"An ERROR occurred {ex}. Aborting automation for hypervisor {self.request.hypervisor}"
            print(msg)
            self.jira.add(msg)
            self.jira.send_buffer()
            #self.jira.move_to_adoption_failed()



    def _run_noops(self):
        """
        do nothing, just to test all objects are created properly
        """
        pass


#    def _run_finish(self):
#        self._finish_icinga()
#        self._finish_alertmanager()
#
#
#    def _finish_icinga(self):
#        hv_icinga = HVIcinga(self.creds_handler, self.request.hypervisor)
#        hv_icinga.remove_downtime()
#        msg = "downtime removed from Icinga"
#        self.jira.add(msg)
#
#    def _finish_alertmanager(self):
#        hv_alertmanager = HVAlertManager(self.creds_handler, self.request.hypervisor)
#        hv_alertmanager.remove_silence()
#        msg = "silence removed from AlertManager"
#        self.jira.add(msg)

