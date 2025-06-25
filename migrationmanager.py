from credentialshandler import CredentialsHandler
from hypervisormanager import HyperVisorManager
from timeinterval import TimeInterval

import threading


class Request:
    def __init__(self, hypervisor, jira_issue_key):
        self.hypervisor = hypervisor
        self.jira_issue_key = jira_issue_key


class MigrationManager:
    def __init__(self, creds_file, hypervisors_file):
        self.creds_file = creds_file
        self.credentials_handler = CredentialsHandler(self.creds_file)
        self.hypervisors_file = hypervisors_file
        self.request_l = self._parse_hypervisors_file()
        self.time_interval = TimeInterval()

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
            hv_manager = HyperVisorManager(self, self.credentials_handler, request, self.time_interval)
            hv_manager.run(step)

    def parallel_run(self, step):
        threads = []
        for request in self.request_l:
            hv_manager = HyperVisorManager(self, self.credentials_handler, request, self.time_interval)
            thread = threading.Thread(target=hv_manager.run, args=(step,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()



