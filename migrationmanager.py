from credentialshandler import CredentialsHandler
from hypervisormanager import HyperVisorManager
from timeinterval import TimeInterval
from hvjira import HVJira

import logging
import logging.handlers
import time
from datetime import datetime


class Request:
    def __init__(self, hypervisor, jira_issue_key):
        self.hypervisor = hypervisor
        self.jira_issue_key = jira_issue_key


class MigrationManager:
    def __init__(self, creds_file, hypervisors_file):
        self.creds_file = creds_file
        self.credentials_handler = CredentialsHandler(self.creds_file)
        self.hypervisors_file = hypervisors_file
        self._setup_login()
        self.request_l = self._parse_hypervisors_file()
        self.time_interval = TimeInterval()
        self.jira = HVJira(self.credentials_handler)

    def _setup_login(self):
        self.log = logging.getLogger()
        logname = f'./logs/{self.hypervisors_file}.{datetime.now().strftime("%Y_%m_%d_%H_%M")}'
        logStream = logging.FileHandler(filename=logname)
        FORMAT='%(asctime)s (UTC) [ %(levelname)s ] %(name)s %(filename)s:%(lineno)d %(funcName)s(): %(message)s'
        formatter = logging.Formatter(FORMAT)
        formatter.converter = time.gmtime  # to convert timestamps to UTC
        logStream.setFormatter(formatter)
        self.log.addHandler(logStream)
        self.log.setLevel(logging.DEBUG) 

    def _parse_hypervisors_file(self):
        results = []
        # Open the file in read mode
        with open(self.hypervisors_file, 'r') as file:
            # Iterate over each line in the file
            for line in file:
                # Remove leading and trailing whitespace
                stripped_line = line.strip()
                # If the line is empty or the first non-blank character is '#', skip it
                if not stripped_line or stripped_line.startswith('#'):
                    continue
                # Split the line by whitespace
                words = stripped_line.split()
                results.append(Request(*words))
        return results

    def run(self, step):
        for request in self.request_l:
            hv_manager = HyperVisorManager(self.credentials_handler, request, self.time_interval, self.jira)
            hv_manager.run(step)

