import paramiko
import os
from getpass import getpass

from logger import SetLogger

class HVSSH(SetLogger):
    def __init__(self, hypervisormanager):
        self._set_logger()
        self.creds_handler = hypervisormanager.creds_handler
        self.hostname = hypervisormanager.request.hypervisor
        self.ssh_private_key_path = self.creds_handler.ssh.key_path
        self.ssh_public_key_path = self.ssh_private_key_path + '.pub'
        self.ssh_username = self.creds_handler.ssh.username
        self.ssh_passphrase = self.creds_handler.ssh.passphrase
        self.jira = hypervisormanager.jira
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.private_key = paramiko.RSAKey.from_private_key_file(self.ssh_private_key_path, password=self.ssh_passphrase)


    def run(self, cmd, username=None):
        self.log.debug('starting run')
        try:
            self._run(cmd, username)
        except Exception as ex:
            msg = f'Exception captured: {ex}'
            self.log.debug(msg)
            self.jira.add("Exception captured")
            self.jira.add_block(ex)
            self.jira.add_comment()
        self.log.debug('leaving run')

    def _run(self, cmd, username=None):
        if not username:
            # if not username is passed, e.g. "root", 
            # we SSH as the regular user set in creds.yaml
            username = self.creds_handler.ssh.username
        self.client.connect(hostname=self.hostname, port=22, username=self.ssh_username, pkey=self.private_key)
        stdin, stdout, stderr = self.client.exec_command(cmd)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        rc = stdout.channel.recv_exit_status()
        self.client.close()
        return output, error, rc

    
    @property
    def has_root_access(self):
        try:
            self.client.connect(self.hostname, username="root", key_filename=self.ssh_private_key_path, timeout=5)
            self.client.exec_command("true")  # Simple command to confirm access
            return True
        except Exception:
            return False


    def ensure_root_access(self):

        if self.has_root_access:
            msg = f"user {self.username} has root acccess to hypervisor {self.hostname}"
            self.log.debug(msg)
            self.jira.add_comment(msg)
            return

        # if not root access...
        # Connect as regular user
        self.client.connect(self.hostname, username=self.username, key_filename=self.ssh_private_key_path)
        # Append the public key to /root/.ssh/authorized_keys via sudo

        # Read your public SSH key
        with open(self.ssh_public_key_path, "r") as pubkey_file:
            public_key = pubkey_file.read().strip()

        command = f"""
        sudo -S su -c 'mkdir -p /root/.ssh && \
        touch /root/.ssh/authorized_keys && \
        grep -qF "{public_key}" /root/.ssh/authorized_keys || echo "{public_key}" >> /root/.ssh/authorized_keys && \
        chmod 700 /root/.ssh && chmod 600 /root/.ssh/authorized_keys'
        """
        stdin, stdout, stderr = self.client.exec_command(command)
        stdin.flush()
        client.close()
