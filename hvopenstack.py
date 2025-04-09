import openstack

from logger import SetLogger

class HVOpenstack(SetLogger):
    def __init__(self, creds_handler, hostname, time_interval=None):
        self._set_logger()
        self.creds_handler = creds_handler
        self.hostname = hostname
        self.time_interval = time_interval
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
                out = (hypervisor.satus.lower() == "enabled")
                break
        self.log.debug(f'leaving is_enabled with value {out}')
        return out


    def disable_service(self):
        self.log.debug('starting disable_service')
        disable_reason = f"RL9 Reinstall {self.time_interval.start_str} - JCB"
        try:
            response = self.conn.compute.disable_service(
                host=self.hostname,
                binary=self.binary_type,
                reason=disable_reason
            )
            self.log.debug(f"Service '{self.binary_type}' on host '{self.hostname}' disabled successfully.")
            # The 'response' object may contain additional info depending on your OpenStack version.
            self.log.debug(f"Response: {response}")
        except Exception as e:
            self.log.debug(f"Failed to disable service '{self.binary_type}' on host '{self.hostname}': {e}")
            raise e
        self.log.debug('leaving disable_service')
