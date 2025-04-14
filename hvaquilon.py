import paramiko

from logger import SetLogger


class HVAquilon(SetLogger):
    def __init__(self, hypervisormanager):
        self._set_logger()
        self.creds_handler = hypervisormanager.creds_handler
        self.jira = hypervisormanager.hvjira
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def run(self, cmd):
        self.log.debug('starting run')
        self.client.connect(hostname="aquilon.gridpp.rl.ac.uk", username=self.creds_handler.aquilon.username, password=self.creds_handler.aquilon.password)
        aqcmd = "export AQHOST=aquilon.gridpp.rl.ac.uk; export AQSERVICE=aqd;"
        aqcmd += "export PATH=/opt/aquilon/bin/:$PATH;"
        aqcmd += cmd
        stdin, stdout, stderr = self.client.exec_command(aqcmd)
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        rc = stdout.channel.recv_exit_status()
        self.client.close()
        self.log.debug('leaving run')
        return output, error, rc


