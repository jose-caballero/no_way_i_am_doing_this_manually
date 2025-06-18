import subprocess

from logger import SetLogger

class HVLocal(SetLogger):
    def __init__(self, hypervisormanager):
        self._set_logger()
        self.creds_handler = hypervisormanager.creds_handler
        self.hostname = hypervisormanager.request.hypervisor
        self.jira = hypervisormanager.jira

    def check_hv_empty(self):
        cmd = f"openstack --os-cloud admin server list --host {self.hostname} --all-projects"
        out, err, rc = self._execute(cmd)
        self.jira.add("checking the HV is empty")
        self.jira.add("executing command:")
        self.jira.add_block(cmd)
        self.jira.add("output:")
        self.jira.add_block(out)
        self.jira.send_buffer()
        if out != "":
            raise Exception("Hypervisor is not empty!!")

    def _execute(self, cmd):
        subproc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True)
        (out, err) = subproc.communicate()
        rc = subproc.returncode
        return out.strip(), err.strip(), rc
