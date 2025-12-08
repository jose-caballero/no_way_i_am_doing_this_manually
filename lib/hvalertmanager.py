import json
import requests
import sys
from lib.hvexception import HVException



class HVAlertManager:
    def __init__(self, hypervisormanager):
        """
        class to create and manage AlertManager silences for a HyperVisor
        initialises with credentials from hypervisormanager object

        param hypervisormanager: HyperVisorManager
        """
        self.creds_handler = hypervisormanager.creds_handler
        self.hostname = hypervisormanager.hostname
        self.alertmanager_url = "https://openstack.stfc.ac.uk:9093"
        self.time_interval = hypervisormanager.time_interval
        self.jira = hypervisormanager.jira

    def create_silence(self):
        """
        Wrapper to create a silence and handle errors
        """
        try:
            self._create_silence()
        except Exception as ex:
            msg = f'Exception captured: {ex}'
            self.jira.add("Exception captured")
            self.jira.add_block(ex)
            self.jira.send_buffer()
            raise HVException(msg)

    def _create_silence(self):
        """
        Create silences for both ``hostname`` and ``instance`` labels.
        """
        silence_data_hostname = {
            "matchers": [
                {"name": "hostname",
                 "value": self.hostname,
                 "isRegex": False},
            ],
            "startsAt": self.time_interval.start_str,
            "endsAt": self.time_interval.end_str, 
            "createdBy": "admin",
            "comment": f"RL9 Reinstall {self.time_interval.start_str} - {self.creds_handler.general.initials}"
        }
        silence_data_instance = {
            "matchers": [
                {"name": "instance",
                 "value": self.hostname,
                 "isRegex": False},
            ],
            "startsAt": self.time_interval.start_str,
            "endsAt": self.time_interval.end_str, 
            "createdBy": "admin",
            "comment": f"RL9 Reinstall {self.time_interval.start_str} - {self.creds_handler.general.initials}"
        }
        response = self._create_silence_matcher(silence_data_hostname)
        out_msg = f"Silence for hostname: {self.alertmanager_url}/#/silences/{response.json()['silenceID']}"
        response = self._create_silence_matcher(silence_data_instance)
        out_msg += "\n"
        out_msg += f"Silence for instance: {self.alertmanager_url}/#/silences/{response.json()['silenceID']}"
        msg = f"silence created in AlertManager successfully, from {self.time_interval.start_str} to {self.time_interval.end_str}"
        msg += "\n"
        msg += out_msg
        self.jira.add(msg)
        self.jira.send_buffer()


    def _create_silence_matcher(self, silence_data):
        """
        send a POST request to create a single Silence
        """
        silences_endpoint = f"{self.alertmanager_url}/api/v2/silences"
        # Make a POST request to the Alertmanager API with basic auth
        headers = {"Content-Type": "application/json"}
        from requests.auth import HTTPBasicAuth
        basic = HTTPBasicAuth(self.creds_handler.alertmanager.username, self.creds_handler.alertmanager.password)
        response = requests.post(silences_endpoint, auth=basic, json=silence_data, headers=headers)
    
        if response.status_code != 200:
            msg = f"Failed to create silence. Response status code: {response.status_code}"
            self.jira.add(msg)
            text = f"Response text: {response.text}"
            self.jira.add_block(response.text)
            self.jira.send_buffer()
            raise HVException(response.text)
        else:
            msg = f"Silence created successfully"
            return response


    def remove_silence(self):
        raise NotImplementedError



