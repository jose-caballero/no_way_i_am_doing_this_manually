import pynetbox
from hvexception import HVException



class HVNetbox:
    def __init__(self, hypervisormanager):
        """
        Wrapper around the NetBox API for a specific HyperVisor

        Parameters
        ----------
        hypervisormanager : HyperVisorManager
            Manager providing credentials and target host information.
        """
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


    def hv_in_netbox(self):
        """
        Validate that the hypervisor exists in NetBox
        """
        if not self.device:
            self.jira.add("there is no info in NetBox for this hypervisor")
            self.jira.send_buffer()
            raise HVException("there is no info in NetBox for this hypervisor")

    def check_status_pre_drain(self):
        """
        Check the device status before draining.
        Returns
        -------
        str
            The status value if it is ``active`` or ``offline``.
        Raises
        ------
        HVException
            If the status is neither ``active`` nor ``offline``.
        """
        data = dict(self.device)
        status = data['status']['value'].lower()
        if status in ["active", "offline"]:
            msg = f"status of hypervisor {self.hostname} in Netbox is {status}, Ready to start."
            self.jira.add(msg)
            self.jira.send_buffer()
            return status
        msg = f"status of hypervisor {self.hostname} in Netbox is neither Active nor Offline. Aborting."
        self.jira.add(msg)
        self.jira.send_buffer()
        raise HVException(msg)

    def change(self, changes_d):
        """
        Apply one or more changes to the NetBox device entry
        and handle errors
        """
        try:
            self._change(changes_d)
        except Exception as ex:
            msg = f'Exception captured: {ex}'
            self.jira.add("Exception captured")
            self.jira.add_block(ex)
            self.jira.send_buffer()
            raise ex

    def _change(self, changes_d):
        """
        Dispatch change operations based on the provided dictionary
        """
        for k,v in changes_d.items():
            if k == "role":
                self._change_role(v)
            if k == "status":
                self._change_status(v)

    def _change_role(self, new_role):
        """
        Change the device role in NetBox
        """
        role = self.conn.dcim.device_roles.get(name=new_role)
        if not role:
            return
        # Assign the retrieved role object
        ###self.device.device_role = role
        self.device.role = role
        self.device.save()
        msg = f"Successfully updated role for device '{self.hostname}' to '{new_role}'"
        msg += "\n"
        msg += self.url
        self.jira.add(msg)
        self.jira.send_buffer()
        
    def _change_status(self, new_status):
        """
        Change the device status in NetBox
        """
        self.device.status = new_status
        self.device.save()
        msg = f"Successfully updated status for device '{self.hostname}' to '{new_status}'"
        msg += "\n"
        msg += self.url
        self.jira.add(msg)
        self.jira.send_buffer()

    @property
    def ipmi_address(self):
        """
        Return the IPMI address of the device
        """
        interfaces = self.conn.dcim.interfaces.filter(device_id=self.device.id)
        for i in interfaces:
            if i.name == "bmc0":
                ip_assignments = self.conn.ipam.ip_addresses.filter(interface_id=i.id)
                return next(ip_assignments).address.split('/')[0]

    @property
    def url(self):
        """
        Return the NetBox web URL for the device
        """
        return f'{self.netbox_url}/dcim/devices/{self.device.id}/'




