import json
import requests
import sys


class HVAlertManager:
    def __init__(self, creds_handler, hostname, time_interval=None):
        self.creds_handler = creds_handler
        self.hostname = hostname
        self.alertmanager_url = "https://openstack.stfc.ac.uk:9093"
        self.time_interval = time_interval

    def create_silence(self):
        silences_endpoint = f"{self.alertmanager_url}/api/v2/silences"
    
        try:
            # Create a new silence
            silence_data = {
                "matchers": [
                    {"name": "hostname",
                     "value": self.hostname,
                     "isRegex": False},
                    {"name": "instance",
                     "value": self.hostname,
                     "isRegex": False},
                ],
                "startsAt": self.time_interval.start_str,
                "endsAt": self.time_interval.end_str, 
                "createdBy": "admin",
                "comment": f"RL9 Reinstall {self.time_interval.start_str} - JCB"
            }

            # Make a POST request to the Alertmanager API with basic auth
            headers = {"Content-Type": "application/json"}
            from requests.auth import HTTPBasicAuth
            basic = HTTPBasicAuth(self.creds_handler.alertmanager.username, self.creds_handler.alertmanager.password)
            response = requests.post(silences_endpoint, auth=basic, json=silence_data, headers=headers)
    
            if response.status_code != 200:
                print("Failed to create silence. Response status code:", response.status_code)
                print("Response text:", response.text)
            else:
                print(f"Silence successfully created: {response.json()}")
    
        except requests.exceptions.RequestException as e:
            print(f"Failed to create silence in Alertmanager: {e}")
            if e.response is not None:
                print("Response status code:", e.response.status_code)
                print("Response text:", e.response.text)
        except Exception as e:
            print(f"An error occurred while creating the silence: {e}")


    def remove_silence(self):
        raise NotImplementedError




