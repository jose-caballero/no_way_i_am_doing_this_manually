import openstack
from datetime import datetime

from logger import SetLogger


class Server:
    def __init__(self, server, conn):
        self.server = server
        self.conn = conn

    @property
    def id(self):
        return self.server.id

    @property
    def can_be_migrated(self):
        if self.server.flavor.name.startswith("g-") or self.server.flavor.name.startswith("f-"):
            return False
        if self.server.status not in ["ACTIVE", "SHUTOFF"]:
            return False
        if self.server.flavor.vcpus > 60:
            return False
        return True

    def snapshot(self):
        """
        Creates a snapshot image of a server
        :return: Snapshot Image
        """

        current_time = datetime.now().strftime("%d-%m-%Y-%H%M")
        image = conn.compute.create_server_image(
            server=self.id,
            name=f"stackstorm-{self.id}-{current_time}",
            wait=True,
            timeout=21600,  # 6 Hours
        )
        wait_for_image_status(conn, image, "active")
        # Make VM's project image owner
        conn.image.update_image(image, owner=self.server.project_id)
        return image

    def migrate(self):
        self.conn.compute.live_migrate_server(
            server=self.id, 
            host=dest_host, 
            block_migration=True
        )



class HVOpenstack(SetLogger):
    def __init__(self, hypervisormanager):
        self._set_logger()
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
   
    @property
    def servers(self):
        """
        return the list of VMs in this hypervisor
        """
        out = []
        servers = list(self.conn.compute.servers(all_projects=True))
        for server in servers:
            if server.hypervisor_name == self.hostname:
                out.append(server)
        return out 

   
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
        try:
            self.log.debug('starting disable_service')
            self._disable_service()
            self.log.debug('leaving disable_service')
        except Exception as ex:
            msg = f'Exception captured: {ex}'
            self.log.debug(msg)
            self.jira.add("Exception captured")
            self.jira.add_block(ex)
            self.jira.send_buffer()
            raise ex

    def _disable_service(self):
        if not self.is_enabled:
            msg = "the hypervisor was already disabled from OpenStack. Nothing to do"
            self.log.debug(msg)
            self.jira.add(msg)
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
        self.jira.send_buffer()


