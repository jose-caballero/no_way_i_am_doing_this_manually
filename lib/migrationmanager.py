from lib.credentialshandler import CredentialsHandler
from lib.hypervisormanager import HyperVisorManager
from lib.timeinterval import TimeInterval
from lib.hypervisorgroup import HyperVisorGroup

class MigrationManager:
    def __init__(self, creds_file, hypervisors_file):
        """
        Read HyperVisor lists and coordinate their processing
        Load credentials and parse the list of HyperVisors
        """
        self.time_interval = TimeInterval()
        self.credentials_handler = CredentialsHandler(creds_file)
        self.hvgroup = self._parse_hypervisors_file(hypervisors_file)

    def _parse_hypervisors_file(self, hypervisors_file):
        # Open the file in read mode
        hvgroup = HyperVisorGroup(self)
        with open(hypervisors_file, 'r') as file:
            # Iterate over each line in the file
            for line in file:
                # Remove leading and trailing whitespace
                stripped_line = line.strip()
                # If the line is empty or the first non-blank character is '#', skip it
                if not stripped_line or stripped_line.startswith('#'):
                    continue
                # Split the line by whitespace
                (hostname, jira_issue_key) = stripped_line.split()
                hv = HyperVisorManager(self, hostname, jira_issue_key)
                hvgroup.append(hv)
        return hvgroup

    def run(self, step):
        self.hvgroup.run(step)


