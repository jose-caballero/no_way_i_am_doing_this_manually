from lib.hvalertmanager import HVAlertManager
from lib.hvnetbox import HVNetbox
from lib.hvopenstack import HVOpenstack
from lib.hvssh import HVSSH
from lib.hvaquilon import HVAquilon
from lib.hvkayobe import HVKayobe
from lib.hvjira import HVJira
from lib.hvexception import HVException

class HyperVisorManager:
    def __init__(self, migration_manager, hostname, jira_issue_key):
        """
        High level orchestration for HyperVisor migration steps
        Coordinate the various services used to migrate a HyperVisor
        Initialise and create helpers for the target HyperVisor
        """
        self.migration_manager = migration_manager
        self.hostname = hostname
        self.jira_issue_key = jira_issue_key
        self.creds_handler = migration_manager.credentials_handler
        self.time_interval = migration_manager.time_interval
        self.jira = HVJira(self)
        self.hvalertmanager = HVAlertManager(self)
        self.hvnetbox = HVNetbox(self)
        self.hvopenstack = HVOpenstack(self)
        self.hvaquilon = HVAquilon(self)
        self.hvssh = HVSSH(self)
        self.hvkayobe = HVKayobe(self)


    def setup(self):
        try:
            self.hvssh.ensure_root_access()
        except HVException as ex:
            msg = f"An ERROR occurred {ex}. Aborting automation for hypervisor {self.hostname}"
            print(msg)

    def pre_drain(self):
        try:
            self.hvssh.is_rocky_8()
            self.hvssh.update_qemu_kvm()
            self.hvnetbox.hv_in_netbox()
            self.hvnetbox.check_status_pre_drain()
            self.hvopenstack.disable_hv()
            self.hvopenstack.show_hv()
            self.hvssh.virsh_info()
        except HVException as ex:
            msg = f"An ERROR occurred {ex}. Aborting automation for hypervisor {self.hostname}"
            print(msg)
            self.jira.add(msg)
            self.jira.send_buffer()
            self.jira.move_to_pre_reinstall_failed()


    def pre_reinstall(self):
        try:
            #self.jira.move_to_working_on_pre_bios()
            self.hvopenstack.ensure_hv_has_no_servers()
            self.hvssh.is_empty()
            self.hvssh.blocks_info()
            if self.hvnetbox.has_gpu:
                self.hvssh.gpus_info()
            self.hvalertmanager.create_silence()
            self.hvnetbox.change({"status":"planned"})
            self.hvssh.mellanox_info()
            self.hvaquilon.reimport()
            self.hvaquilon.remove_interfaces()
            self.hvaquilon.remove_sata_disk()
            self.hvaquilon.make_host()
            self.hvaquilon.pxeswitch_host()
            if self.hvssh.mellanox_info() != "":
                self.hvkayobe.run_mellanox_playbook()
            self.hvnetbox.report_ipmi_address()
            #self.jira.move_to_ready_for_reinstall()
        except HVException as ex:
            msg = f"An ERROR occurred {ex}. Aborting automation for hypervisor {self.hostname}"
            print(msg)
            self.jira.add(msg)
            self.jira.send_buffer()
            self.jira.move_to_pre_bios_failed()

    def post_reinstall(self):
        try:
            #self.jira.move_to_working_on_post_reinstall()
            self.hvssh.is_rocky_9()
            self.hvssh.blocks_info()
            if self.hvnetbox.has_gpu:
                self.hvssh.gpus_info()
            self.hvssh.verify_is_efi()
            self.hvssh.hardware_specific()
            self.hvnetbox.change({"status":"active", "role":"Openstack Prod Kolla_Compute"})
            #self.jira.move_to_ready_for_adoption()
        except HVException as ex:
            msg = f"An ERROR occurred {ex}. Aborting automation for hypervisor {self.hostname}"
            print(msg)
            self.jira.add(msg)
            self.jira.send_buffer()


    def noops(self):
        """
        do nothing, just to test all objects are created properly
        """
        print(self.hostname)

