import json
import requests
import sys

from logger import SetLogger


class HVAlertManager(SetLogger):
    def __init__(self, hypervisormanager):
        self._set_logger()
        self.creds_handler = hypervisormanager.creds_handler
        self.hostname = hypervisormanager.request.hypervisor
        self.alertmanager_url = "https://openstack.stfc.ac.uk:9093"
        self.time_interval = hypervisormanager.time_interval
        self.jira = hypervisormanager.hvjira

    def create_silence(self):
        self.log.debug("starting create_silence")
        silence_data_hostname = {
            "matchers": [
                {"name": "hostname",
                 "value": self.hostname,
                 "isRegex": False},
            ],
            "startsAt": self.time_interval.start_str,
            "endsAt": self.time_interval.end_str, 
            "createdBy": "admin",
            "comment": f"RL9 Reinstall {self.time_interval.start_str} - JCB"
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
            "comment": f"RL9 Reinstall {self.time_interval.start_str} - JCB"
        }
        response = self._create_silence(silence_data_hostname)
        out_msg = f"Silence for hostname: {self.alertmanager_url}/#/silences/{response.json()['silenceID']}"
        response = self._create_silence(silence_data_instance)
        out_msg += "\n"
        out_msg += f"Silence for instance: {self.alertmanager_url}/#/silences/{response.json()['silenceID']}"
        self.log.debug('leaving create_silence')
        return out_msg


    def _create_silence(self, silence_data):
        silences_endpoint = f"{self.alertmanager_url}/api/v2/silences"
        try:
            # Make a POST request to the Alertmanager API with basic auth
            headers = {"Content-Type": "application/json"}
            from requests.auth import HTTPBasicAuth
            basic = HTTPBasicAuth(self.creds_handler.alertmanager.username, self.creds_handler.alertmanager.password)
            response = requests.post(silences_endpoint, auth=basic, json=silence_data, headers=headers)
    
            if response.status_code != 200:
                self.log.debug(f"Failed to create silence. Response status code: {response.status_code}")
                self.log.debug(f"Response text: {response.text}")
            else:
                self.log.debug(f"Silence successfully created: {response.json()}")
                return response
        except requests.exceptions.RequestException as e:
            self.log.debug(f"Failed to create silence in Alertmanager: {e}")
            if e.response is not None:
                self.log.debug("Response status code:", e.response.status_code)
                self.log.debug("Response text:", e.response.text)
            raise e
        except Exception as e:
            self.log.debug(f"An error occurred while creating the silence: {e}")
            raise e


    def remove_silence(self):
        raise NotImplementedError




