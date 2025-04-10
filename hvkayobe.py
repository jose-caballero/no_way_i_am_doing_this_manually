import subprocess
import datetime

from logger import SetLogger

class HVKayobe(SetLogger):
    def __init__(self, creds_handler):
        self._set_logger()
        self.creds_handler = creds_handler

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
        self.log.debug('leaving run')
        return out
