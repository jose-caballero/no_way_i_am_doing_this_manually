import openstack

from logger import SetLogger

class HVOpenstack(SetLogger):
    def __init__(self, hypervisormanager):
        self._set_logger()
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
   
    @property
    def is_enabled(self):
        self.log.debug('starting is_enabled')
        hypervisors = self.conn.compute.hypervisors()
        for hypervisor in hypervisors:
            if hypervisor.name == self.hostname:
                out = (hypervisor.status.lower() == "enabled")
                break
        self.log.debug(f'leaving is_enabled with value {out}')
        return out

    def disable_service(self):
        self.log.debug('starting disable_service')
        try:
            self._disable_service()
        except Exception as ex:
            msg = f'Exception captured: {ex}'
            self.log.debug(msg)
            self.jira.add("Exception captured")
            self.jira.add_block(ex)
            self.jira.add_comment()
            raise ex
        self.log.debug('leaving disable_service')

    def _disable_service(self):
        if not self.is_enabled:
            msg = "the hypervisor was already disabled from OpenStack. Nothing to do"
            self.log.debug(msg)
            self.jira.add_comment(msg)
            return
        # if the host is enabled in OpenStack...
        disable_reason = f"RL9 Reinstall {self.time_interval.start_str} - JCB"
        response = self.conn.compute.disable_service(
            host=self.hostname,
            binary=self.binary_type,
            reason=disable_reason
        )
        msg = f"Service '{self.binary_type}' on host '{self.hostname}' disabled successfully."
        response = f"Response: {response}"
        self.log.debug(msg)
        self.log.debug(response)
        self.jira.add(msg)
        self.jira.add_block(response)
        self.jira.add_comment()
