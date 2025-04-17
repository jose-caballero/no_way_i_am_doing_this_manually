import subprocess
import datetime

from logger import SetLogger

class HVKayobe(SetLogger):
    def __init__(self, hypervisormanager):
        self._set_logger()
        self.creds_handler = hypervisormanager.creds_handler
        self.jira = hypervisormanager.jira
        self.hostname = hypervisormanager.request.hypervisor

    def run_mellanox(self):
        cmd = f"~/mellanox_playbook.sh {self.hostname}"
        return self._run(cmd)

    def _run(self, cmd):
        """
        arguments for the remote command:
             path to file with unencrypted SSH key 
             hostname with the kayobe environment
             username to ssh to that host
             command to execute
        """
        self.log.debug('starting run')
        cmd = (
            "eval $(ssh-agent) >/dev/null; "
            f"ssh-add {self.creds_handler.kayobe.nopassfile}; "
            f"ssh -A {self.creds_handler.kayobe.username}@{self.creds_handler.kayobe.hostname} '{cmd}'"
        )
        subproc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True)
        (out, err) = subproc.communicate()
        st = subproc.returncode
        self.log.debug(f'cmd = {cmd}')
        self.log.debug(f'output = {out}')
        self.log.debug(f'err = {err}')
        self.log.debug(f'rc = {st}')
        self.jira.add_comment("command:")
        self.jira.add_block(cmd)
        self.jira.add_comment("output:")
        self.jira.add_block(out)
        self.jira.add_comment("error:")
        self.jira.add_block(err)
        self.jira.add_comment("return code:")
        self.jira.add_block(st)
        self.log.debug('leaving run')
        return out
