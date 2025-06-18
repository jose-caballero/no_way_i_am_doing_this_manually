import subprocess
from logger import SetLogger


class HVLocal(SetLogger):
    def __init__(self, hypervisormanager):
        self._set_logger()
        self.creds_handler = hypervisormanager.creds_handler
        self.hostname = hypervisormanager.request.hypervisor
        self.jira = hypervisormanager.jira

    @property
    def hv_has_no_servers(self):
        cmd = f"openstack --os-cloud admin server list --host {self.hostname} --all-projects"
        self.jira.add("checking the HV is empty")
        out, err, rc = self._execute(cmd)
        return (out == "")

    def disable_hv(self):
        cmd = f'openstack compute service set --disable --disable-reason "Migration to Rocky 9 - JCB" {self.hostname} nova-compute'
        self.jira.add("disabling HV")
        self._execute(cmd)

    def enable_hv(self):
        cmd = f'openstack compute service set --enable {self.hostname} nova-compute'
        self.jira.add("disabling HV")
        self._execute(cmd)


    def _execute(self, cmd):
        subproc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True)
        (out, err) = subproc.communicate()
        rc = subproc.returncode
        self.jira.add("executing command:")
        self.jira.add_block(cmd)
        self.jira.add("output:")
        self.jira.add_block(out)
        self.jira.add("error:")
        self.jira.add_block(err)
        self.jira.add("rc:")
        self.jira.add_block(rc)
        self.jira.send_buffer()
        return out.strip(), err.strip(), rc
