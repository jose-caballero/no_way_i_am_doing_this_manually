import openstack
from datetime import datetime
from hvlocal import run


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
        self.hostname = hypervisormanager.request.hypervisor
        self.time_interval = hypervisormanager.time_interval
        self.jira = hypervisormanager.jira
        self.binary_type = "nova-compute"
        self.conn = openstack.connection.Connection(
            auth_url = "https://openstack.stfc.ac.uk:5000/v3", 
            project_name = self.creds_handler.openstack.cloud,  
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
        if self.list_servers:
            raise HVException("hypervisor still not empty")

    def disable_hv(self):
        """
        Disable the HyperVisor service in OpenStack
        """
        cmd = f'openstack --os-cloud {self.creds_handler.openstack.cloud} compute service set --disable --disable-reason "Migration to Rocky 9 - JCB" {self.hostname} nova-compute'
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
        cmd = f'openstack --os-cloud admin hypervisor show {self.hostname}'
        self.jira.add("full status of the HV")
        results = run(cmd)
        self.jira.add(results.report_to_jira)
        self.jira.send_buffer()


    def list_servers(self):
        """
        if the HV is not empty, list the servers

        NOTE: alternative using query library

                q = ServerQuery()
                q.select("id")
                q.where(preset="equal", prop="hypervisor_name", value=self.hostname
                q.run("admin", as_admin=True, all_projects=True)
                out = q.to_string()
                self.jira.add_block(out)
                self.jira.send_buffer()
        """
        cmd = f"openstack --os-cloud {self.creds_handler.openstack.cloud} server list --host {self.hostname} --all-projects"
        self.jira.add("listing servers in HV")
        results = run(cmd)
        self.jira.add(results.report_to_jira)
        self.jira.send_buffer()
        # returns True if the HV has servers
        #         False if the HV is empty
        return (results.stdout != "")


