import requests
import sys
import argparse
import time

from logger import SetLogger

# Disable SSL warnings (use with caution in production environments)
requests.packages.urllib3.disable_warnings()


class HVIcinga(SetLogger):

    def __init__(self, hypervisormanager):
        self._set_logger()
        self.api_url = "https://icinga.scd.stfc.ac.uk:5665"
        self.creds_handler = hypervisormanager.creds_handler
        self.hostname = hypervisormanager.request.hypervisor
        self.time_interval = hypervisormanager.time_interval

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
                self.log.debug(f"Unexpected response from API: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.log.debug(f"Error connecting to Icinga API: {e}")
            return False

    def create_downtime(self):
        self.log.debug('starting create_downtime')
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
        response = requests.post(
            url,
            json=payload,
            auth=(self.creds_handler.icinga_downtime.username, self.creds_handler.icinga_downtime.password),
            headers={"Accept": "application/json"},
            verify=False  # Replicates '-k' to ignore SSL certificate
        )
        # If request is successful, respond with "OK", otherwise "failed"
        if response.ok:
            self.log.debug("OK")
        else:
            self.log.debug("failed")
        self.log.debug('leaving create_downtime')
        return response


    def remove_downtime(self):
        raise NotImplementedError 


