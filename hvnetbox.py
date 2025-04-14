import pynetbox
import json

from logger import SetLogger

class HVNetbox(SetLogger):
    def __init__(self, hypervisormanager):
        self._set_logger()
        self.creds_handler = hypervisormanager.creds_handler
        self.hostname = hypervisormanager.request.hypervisor 
        self.jira = hypervisormanager.hvjira
        self.netbox_url = "https://netbox.esc.rl.ac.uk/"
        self.conn = pynetbox.api(
            self.netbox_url,
            token = self.creds_handler.netbox.api_token
        )
        # Retrieve the device by name (returns None if not found)
        self.device = self.conn.dcim.devices.get(name=self.hostname)
        if not self.device:
            self.log.debug(f"No device found with name '{self.hostname}'")

    def change_role(self, new_role):
        self.log.debug('starting change_role')
        new_role = new_role.lower()
        role = self.conn.dcim.device_roles.get(name=new_role)
        if not role:
            self.log.debug("Could not find the specified role in NetBox.")
            self.log.debug('leaving change_role')
            return
        try:
            # Assign the retrieved role object
            self.device.device_role = role
            self.device.role = role
            self.device.save()
            self.log.debug(f"Successfully updated role for device '{self.hostname}' to '{new_role}'")
        except pynetbox.RequestError as e:
            self.log.debug(f"Failed to update the device role: {e}")
            raise e
        self.log.debug('leaving change_role')
        
    def change_status(self, new_status):
        try:
            self.device.status = new_status
            self.device.save()
            self.log.debug(f"Successfully updated status for device '{self.hostname}' to '{new_status}'")
        except pynetbox.RequestError as e:
            self.log.debug(f"Failed to update the device status: {e}")
            raise e

    @property
    def ipmi_address(self):
        interfaces = self.conn.dcim.interfaces.filter(device_id=self.device.id)
        for i in interfaces:
            if i.name == "bmc0":
                ip_assignments = self.conn.ipam.ip_addresses.filter(interface_id=i.id)
                return next(ip_assignments).address

    @property
    def url(self):
        return f'{self.netbox_url}/dcim/devices/{self.device.id}/'


