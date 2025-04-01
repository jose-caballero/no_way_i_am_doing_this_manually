import paramiko


class HVSSH:
    def __init__(self, creds_handler, hostname):
        self.creds_handler = creds_handler
        self.hostname = hostname
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.private_key = paramiko.RSAKey.from_private_key_file(self.creds_handler.ssh.key_path, password=self.creds_handler.ssh.passphrase)

    def run(self, cmd):
        self.client.connect(hostname=self.hostname, port=22, username=self.creds_handler.ssh.username, pkey=self.private_key)
        stdin, stdout, stderr = self.client.exec_command(cmd)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        rc = stdout.channel.recv_exit_status()
        self.client.close()
        return output, error, rc


