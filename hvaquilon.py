import paramiko

from logger import SetLogger


class HVAquilon(SetLogger):
    def __init__(self, hypervisormanager):
        self._set_logger()
        self.creds_handler = hypervisormanager.creds_handler
        self.jira = hypervisormanager.jira
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def run(self, cmd):
        try:
            self.log.debug('starting run')
            self._run(cmd)
            self.log.debug('leaving run')
        except Exception as ex:
            msg = f'Exception captured: {ex}'
            self.log.debug(msg)
            self.jira.add("Exception captured")
            self.jira.add_block(ex)
            self.jira.add_comment()
            raise ex

    def _run(self, cmd):
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
        self.log.debug(f'cmd = {aqcmd}')
        self.log.debug(f'output = {output}')
        self.log.debug(f'error = {error}')
        self.log.debug(f'rc = {rc}')
        self.jira.add_comment("command:")
        self.jira.add_block(aqcmd)
        self.jira.add_comment("output:")
        self.jira.add_block(output)
        self.jira.add_comment("error:")
        self.jira.add_block(error)
        self.jira.add_comment("return code:")
        self.jira.add_block(rc)
        self.log.debug('leaving run')
        return output, error, rc


