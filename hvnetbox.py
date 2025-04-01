import pynetbox
import json


class HVNetbox:
    def __init__(self, creds_handler, hostname):
        self.creds_handler = creds_handler
        self.hostname = hostname
        self.netbox_url = "https://netbox.esc.rl.ac.uk/"
        self.conn = pynetbox.api(
            self.netbox_url,
            token = self.creds_handler.netbox.api_token
        )
        # Retrieve the device by name (returns None if not found)
        self.device = self.conn.dcim.devices.get(name=self.hostname)
        if not self.device:
            print(f"No device found with name '{self.hostname}'")

    def change_role(self, new_role):
        new_role = new_role.lower()
        role = self.conn.dcim.device_roles.get(name=new_role)
        if not role:
            print("Could not find the specified role in NetBox.")
            return
        try:
            # Assign the retrieved role object
            self.device.device_role = role
            self.device.role = role
            self.device.save()
            print(f"Successfully updated role for device '{self.hostname}' to '{new_role}'")
        except pynetbox.RequestError as e:
            print(f"Failed to update the device role: {e}")
        
    def change_status(self, new_status):
        try:
            self.device.status = new_status
            self.device.save()
            print(f"Successfully updated status for device '{self.hostname}' to '{new_status}'")
        except pynetbox.RequestError as e:
            print(f"Failed to update the device status: {e}")

