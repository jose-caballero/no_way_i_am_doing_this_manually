import requests
import sys
import argparse
import time


# Disable SSL warnings (use with caution in production environments)
requests.packages.urllib3.disable_warnings()


class HVIcinga:

    def __init__(self, creds_handler, hostname, time_interval=None):
        self.api_url = "https://icinga.scd.stfc.ac.uk:5665"
        self.creds_handler = creds_handler
        self.hostname = hostname
        self.time_interval = time_interval

    @property
    def host_is_registered(self):
        url = f"{self.api_url}/v1/objects/hosts/{self.hostname}"
        try:
            auth = (self.creds_handler.icinga_query.username, self.creds_handler.icinga_query.password)
            response = requests.get(url, auth=auth, verify=False)
            if response.status_code == 200:
                return True
            elif response.status_code == 404:
                return False
            else:
                print(f"Unexpected response from API: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to Icinga API: {e}")
            return False

    def create_downtime(self):
        url = f"{self.api_url}/v1/actions/schedule-downtime"
        payload = {
            "type": "Host",
            "filter": f'host.name=="{self.hostname}"',
            "all_services": True,
            "comment": f"RL9 Reinstall {self.time_interval.start_str} - JCB",
            "author": "admin",
            "fixed": True,
            "start_time": self.time_interval.start_seconds,
            "end_time": self.time_interval.end_seconds
        }

        try:
            response = requests.post(
                url,
                json=payload,
                auth=(self.creds_handler.icinga_downtime.username, self.creds_handler.icinga_downtime.password),
                headers={"Accept": "application/json"},
                verify=False  # Replicates '-k' to ignore SSL certificate
            )
            # If request is successful, respond with "OK", otherwise "failed"
            if response.ok:
                print("OK")
            else:
                print("failed")
            return response
        except Exception as e:
            # In case of any exception, print "failed"
            print("failed")


    def remove_downtime(self):
        raise NotImplementedError 


