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
        self.jira = hypervisormanager.jira

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
        try:
            self.log.debug('starting create_downtime')
            self._create_downtime()
            self.log.debug('leaving create_downtime')
        except Exception as ex:
            msg = f'Exception captured: {ex}'
            self.log.debug(msg)
            self.jira.add("Exception captured")
            self.jira.add_block(ex)
            self.jira.add_comment()
            raise ex

    def _create_downtime(self):
        if not self.host_is_registered:
            msg = "Hypervisor is not registered in Icinga, no need for downtime."
            self.log.debug(msg)
            self.jira.add_comment(msg)
            return
        # if the hypervisor is registered in Icinga...
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
            downtime_name = response.json()['results'][0]['name']
            msg = f"downtime in Icinga created successfully, from {self.time_interval.start_str} to {self.time_interval.end_str}. Downtime name: {downtime_name}"
            self.log.debug(msg)
            self.jira.add_comment(msg)
        else:
            msg = f"creating downtime from {self.time_interval.start_str} to {self.time_interval.end_str} failed: {response.text}"
            self.log.debug(msg)
            self.jira.add_comment(msg)


    def remove_downtime(self):
        raise NotImplementedError 

