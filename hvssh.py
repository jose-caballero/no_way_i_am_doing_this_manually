import paramiko

from logger import SetLogger

class HVSSH(SetLogger):
    def __init__(self, hypervisormanager):
        self._set_logger()
        self.creds_handler = hypervisormanager.creds_handler
        self.hostname = hypervisormanager.request.hypervisor
        self.jira = hypervisormanager.hvjira
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.private_key = paramiko.RSAKey.from_private_key_file(self.creds_handler.ssh.key_path, password=self.creds_handler.ssh.passphrase)

    def run(self, cmd, username=None):
        self.log.debug('starting run')
        if not username:
            # if not username is passed, e.g. "root", 
            # we SSH as the regular user set in creds.yaml
            username = self.creds_handler.ssh.username
        self.client.connect(hostname=self.hostname, port=22, username=username, pkey=self.private_key)
        stdin, stdout, stderr = self.client.exec_command(cmd)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        rc = stdout.channel.recv_exit_status()
        self.client.close()
        self.log.debug('leaving run')
        return output, error, rc


