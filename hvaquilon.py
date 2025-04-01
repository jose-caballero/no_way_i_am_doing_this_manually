import paramiko



class HVAquilon:
    def __init__(self, creds_handler):
        self.creds_handler = creds_handler
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def run(self, cmd):
        self.client.connect(hostname="aquilon.gridpp.rl.ac.uk", username=self.creds_handler.aquilon.username, password=self.creds_handler.aquilon.password)
        aqcmd = "export AQHOST=aquilon.gridpp.rl.ac.uk; export AQSERVICE=aqd;"
        aqcmd += "export PATH=/opt/aquilon/bin/:$PATH;"
        aqcmd += cmd
        stdin, stdout, stderr = self.client.exec_command(aqcmd)
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        rc = stdout.channel.recv_exit_status()
        self.client.close()
        return output, error, rc


