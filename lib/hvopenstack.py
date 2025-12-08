import openstack
from datetime import datetime
from lib.hvlocal import run
import time


class Server:
    def __init__(self, hvopenstack, server_id):
        """
        class to handle a single Server (VM)
        :param hvopenstack: a reference to the HVOpenstack instance that created this object
        :param server_id: the ID of the VM
        """
        self.hypervisormanager = hvopenstack.hypervisormanager
        self.creds_handler = self.hypervisormanager.creds_handler
        self.jira = self.hypervisormanager.jira
        self.server_id = server_id

    @property
    def status(self):
        cmd = f'openstack --os-cloud {self.creds_handler.openstack.cloud} server show {self.server_id} -f value -c status'
        results = run(cmd)
        return results.stdout

    @property
    def hypervisor(self):
        cmd = f'openstack --os-cloud {self.creds_handler.openstack.cloud} server show {self.server_id} -f value -c "OS-EXT-SRV-ATTR:hypervisor_hostname"'
        results = run(cmd)
        return results.stdout

###    def migrate(self):
###        """
###        migrate this server
###        """
###        live_migration_flag = '--live-migration' if self.status == "ACTIVE" else ''
###        cmd = f"openstack --os-cloud {self.creds_handler.openstack.cloud} server migrate {live_migration_flag} {self.server_id}"
###        results = run(cmd)
###        self.jira.add(f"triggering the migration of server {self.server_id}")
###        self.jira.add(results.report_to_jira)
###        if results.rc != 0:
###            self.jira.add(f"it seems the server {self.server_id} cannot be migrated. Aborting")
###            self.jira.send_buffer()
###            raise HVException(f'migrating server {self.server_id} has failed.')
###
###        self.jira.add("now we wait for it to finish....")
###        self.jira.send_buffer()
###
###        remaining_time = 3600
###        while remaining_time > 0:
###
###            current_status = self.status
###            if current_status == "ERROR":
###                self.jira.add(f'migrating server {self.server_id} has failed.')
###                self.jira.add("raising an exception to abort")
###                self.jira.send_buffer()
###                raise HVException(f'migrating server {self.server_id} has failed.')
###
###            if self.hypervisor != self.hypervisormanager.request.hypervisor and current_status in ["ACTIVE", "SHUTOFF"]:
###                self.jira.add(f'migrating server {self.server_id} finished OK')
###                cmd = f'openstack --os-cloud {self.creds_handler.openstack.cloud} server show {self.server_id}'
###                results = run(cmd)
###                self.jira.add(results.report_to_jira)
###                self.jira.send_buffer()
###                break 
###
###            time.sleep(10)
###            remaining_time -= 10
###        else:
###            self.jira.add(f'after waiting for a long time, the server {self.server_id} has not been migrated yet.')
###            self.jira.add("raising an exception to abort")
###            self.jira.send_buffer()
###            raise HVException(f'migrating server {self.server_id} has failed.')



class HVOpenstack:
    def __init__(self, hypervisormanager):
        """
        Connect to OpenStack using credentials from ``hypervisormanager``.
        Parameters
        ----------
        hypervisormanager : HyperVisorManager
            Manager providing credentials, hostname and Jira helper.
        """
        self.hypervisormanager = hypervisormanager
        self.creds_handler = hypervisormanager.creds_handler
        self.hostname = hypervisormanager.hostname
        self.time_interval = hypervisormanager.time_interval
        self.jira = hypervisormanager.jira
        self.binary_type = "nova-compute"
        self.conn = openstack.connection.Connection(
            auth_url = "https://openstack.stfc.ac.uk:5000/v3", 
            project_name = "admin",  
            username = self.creds_handler.openstack.username, 
            password = self.creds_handler.openstack.password, 
            user_domain_name = "default",
            project_domain_name = "default", 
            verify=True
        )

    def ensure_hv_has_no_servers(self):
        """
        Ensure that no servers are running on the HyperVisor
        """
        if self.list_servers() != []:
            raise HVException("hypervisor still not empty")
    
    def disable_hv(self):
        """
        Disable the HyperVisor service in OpenStack
        """
        cmd = f'openstack --os-cloud {self.creds_handler.openstack.cloud} compute service set --disable --disable-reason "Migration to Rocky 9 - {self.creds_handler.general.initials}" {self.hostname} nova-compute'
        self.jira.add("disabling HV")
        results = run(cmd)
        self.jira.add(results.report_to_jira)
        self.jira.send_buffer()
    
    def enable_hv(self):
        """
        Re-enable the HyperVisor service in OpenStack
        """
        cmd = f'openstack --os-cloud {self.creds_handler.openstack.cloud} compute service set --enable {self.hostname} nova-compute'
        self.jira.add("enabling HV")
        results = run(cmd)
        self.jira.add(results.report_to_jira)
        self.jira.send_buffer()

    def show_hv(self):
        """
        get the full status of the HyperVisor
        """
        cmd = f'openstack --os-cloud {self.creds_handler.openstack.cloud} hypervisor show {self.hostname}'
        self.jira.add("full status of the HV")
        results = run(cmd)
        self.jira.add(results.report_to_jira)
        self.jira.send_buffer()

    def list_servers(self):
        """
        if the HV is not empty, list the servers
        """
        cmd = f"openstack --os-cloud {self.creds_handler.openstack.cloud} server list --host {self.hostname} --all-projects"
        self.jira.add("listing servers in HV")
        results = run(cmd)
        self.jira.add(results.report_to_jira)
        self.jira.send_buffer()

        # when not empty, output is like this
        #  +--------------------------------------+-----------------+--------+--------------------------+-------+----------+----------------------------------+
        #  | ID                                   | Name            | Status | Networks                 | Image | Flavor   | Project ID                       |
        #  +--------------------------------------+-----------------+--------+--------------------------+-------+----------+----------------------------------+
        #  | 1d8b1126-38e4-4758-9f6c-8d71f185f5a6 | ajh-test-001    | ACTIVE | internal-net=10.10.3.175 |       | c3.small | c9aee696c4b54f12a645af2c951327dc |
        #  | 89a64bb3-5f44-4571-816a-7966ee9044ea | jake-hypervisor | ACTIVE | Internal=172.16.115.131  |       | c3.large | c9aee696c4b54f12a645af2c951327dc |
        #  +--------------------------------------+-----------------+--------+--------------------------+-------+----------+----------------------------------+
        
        servers = []
        out = results.stdout
        if out:
            lines = out.split('\n')
            for line in lines[3:-1]:
                fields = line.split('|')
                server_id = fields[1].strip()
                servers.append( Server(self, server_id) )
        return servers

###    def migrate_servers(self):
###        self.jira.add(f"migrating the servers in HV {self.hostname}")
###        self.jira.send_buffer()
###        for server in self.list_servers():
###            server.migrate()
            
