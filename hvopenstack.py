import openstack
from datetime import datetime
from hvlocal import run


class HVOpenstack:
    def __init__(self, hypervisormanager):
        self.hypervisormanager = hypervisormanager
        self.creds_handler = hypervisormanager.creds_handler
        self.hostname = hypervisormanager.request.hypervisor
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

    def hv_has_no_servers(self):
        cmd = f"openstack --os-cloud admin server list --host {self.hostname} --all-projects"
        self.jira.add("checking the HV is empty")
        results = run(cmd)
        self.jira.add(results.report_to_jira)
        empty = (results.stdout == "")
        self.jira.add(f"HV has no servers? {empty}")
        self.jira.send_buffer()
        if not empty:
            raise HVException("hypervisor still not empty")
    
    def disable_hv(self):
        cmd = f'openstack --os-cloud admin compute service set --disable --disable-reason "Migration to Rocky 9 - JCB" {self.hostname} nova-compute'
        self.jira.add("disabling HV")
        results = run(cmd)
        self.jira.add(results.report_to_jira)
        self.jira.send_buffer()
    
    def enable_hv(self):
        cmd = f'openstack --os-cloud admin compute service set --enable {self.hostname} nova-compute'
        self.jira.add("enabling HV")
        results = run(cmd)
        self.jira.add(results.report_to_jira)
        self.jira.send_buffer()


