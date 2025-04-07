import subprocess
import datetime

from logger import SetLogger

class HVKayobe(SetLogger):
    def __init__(self, creds_handler):
        self._set_logger()
        self.creds_handler = creds_handler

    def run(self, cmd):
        """
        we call an expect script in a subshell
        arguments for the expect scripts:
             password for the ssh agent
             hostname with the kayobe environment
             username to ssh to that host
             command to execute
        """
        self.log.debug('starting run')
        cmd = f"kayobe {self.creds_handler.kayobe.passphrase} {self.creds_handler.kayobe.hostname} {self.creds_handler.kayobe.username} {cmd}"
        subproc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True)
        (out, err) = subproc.communicate()
        end_t = datetime.datetime.now()
        st = subproc.returncode
        self.log.debug('leaving run')
        return out, err, st
