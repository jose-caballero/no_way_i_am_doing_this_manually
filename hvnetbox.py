import pynetbox
import json

from logger import SetLogger

class HVNetbox(SetLogger):
    def __init__(self, hypervisormanager):
        self._set_logger()
        self.creds_handler = hypervisormanager.creds_handler
        self.hostname = hypervisormanager.request.hypervisor 
        self.jira = hypervisormanager.jira
        self.netbox_url = "https://netbox.esc.rl.ac.uk/"
        self.conn = pynetbox.api(
            self.netbox_url,
            token = self.creds_handler.netbox.api_token
        )
        # Retrieve the device by name (returns None if not found)
        self.device = self.conn.dcim.devices.get(name=self.hostname)
        if not self.device:
            self.log.debug(f"No device found with name '{self.hostname}'")

    @property
    def status(self):
        data = dict(self.device)
        return data['status']['value'].lower()

    def change(self, changes_d):
        try:
            self.log.debug("starting change")
            self._change(changes_d)
            self.log.debug("leavingchange")
        except Exception as ex:
            msg = f'Exception captured: {ex}'
            self.log.debug(msg)
            self.jira.add("Exception captured")
            self.jira.add_block(ex)
            self.jira.send_buffer()
            raise ex

    def _change(self, changes_d):
        for k,v in changes_d.items():
            if k == "role":
                self._change_role(v)
            if k == "status":
                self._change_status(v)

    def _change_role(self, new_role):
        self.log.debug('starting change_role')
        role = self.conn.dcim.device_roles.get(name=new_role)
        if not role:
            self.log.debug("Could not find the specified role in NetBox.")
            self.log.debug('leaving change_role')
            return
        # Assign the retrieved role object
        ###self.device.device_role = role
        self.device.role = role
        self.device.save()
        msg = f"Successfully updated role for device '{self.hostname}' to '{new_role}'"
        msg += "\n"
        msg += self.url
        self.log.debug(msg)
        self.jira.add(msg)
        self.jira.send_buffer()
        self.log.debug('leaving change_role')
        
    def _change_status(self, new_status):
        self.log.debug('starting change_status')
        self.device.status = new_status
        self.device.save()
        msg = f"Successfully updated status for device '{self.hostname}' to '{new_status}'"
        msg += "\n"
        msg += self.url
        self.log.debug(msg)
        self.jira.add(msg)
        self.jira.send_buffer()
        self.log.debug('leaving change_status')

    @property
    def ipmi_address(self):
        interfaces = self.conn.dcim.interfaces.filter(device_id=self.device.id)
        for i in interfaces:
            if i.name == "bmc0":
                ip_assignments = self.conn.ipam.ip_addresses.filter(interface_id=i.id)
                return next(ip_assignments).address.split('/')[0]

    @property
    def url(self):
        return f'{self.netbox_url}/dcim/devices/{self.device.id}/'




