import openstack


class HVOpenstack:
    def __init__(self, creds_handler, hostname, time_interval=None):
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
   
    def disable_service(self):
        disable_reason = f"RL9 Reinstall {self.time_interval.start_str} - JCB"
        try:
            response = self.conn.compute.disable_service(
                host=self.hostname,
                binary=self.binary_type,
                reason=disable_reason
            )
            print(f"Service '{self.binary_type}' on host '{self.hostname}' disabled successfully.")
            # The 'response' object may contain additional info depending on your OpenStack version.
            print("Response:", response)
        except Exception as e:
            print(f"Failed to disable service '{self.binary_type}' on host '{self.hostname}': {e}")

