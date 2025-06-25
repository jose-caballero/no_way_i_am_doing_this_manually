import paramiko
from hvexception import HVException
from hvlocal import Results

class HVAquilon:
    def __init__(self, hypervisormanager):
        self.creds_handler = hypervisormanager.creds_handler
        self.jira = hypervisormanager.jira
        self.hostname = hypervisormanager.request.hypervisor
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    @property
    def model(self):
        cmd = f'myaq-get-model {self.hostname}'
        results = self.run(cmd)
        return results.stdout

    def remove_interfaces(self):
        """
        remove interfaces other than bmc0 and eth0
        """
        self.jira.add("Removing unnecessary interfaces from the host on Aquilon")
        cmd = f"python3 ./remove_interfaces.py {self.hostname}"
        results = self.run(cmd)
        self.jira.add(results.report_to_jira)
        self.jira.send_buffer()


    def reimport(self):
        self.jira.add("Executing script to re-import the host on Aquilon")
        cmd = f"./reimport-host.sh {self.hostname}"
        results = self.run(cmd)
        self.jira.add(results.report_to_jira)
        self.jira.send_buffer()
        

    def manage_to_sandbox(self):
        self.jira.add("Manage the host to David's Sandbox on Aquilon")
        cmd = f"aq manage --sandbox ieb35538/point_hvs_to_live_for_rl9_6 --hostname {self.hostname} --force"
        results = self.run(cmd)
        self.jira.add(results.report_to_jira)
        self.jira.send_buffer()

    def prepare_host(self):
        self.jira.add("Recompiling and pxe switching the HV on Aquilon")
        cmd = f"python3 ./prepare_host.py {self.hostname}"
        results = self.run(cmd)
        self.jira.add(results.report_to_jira)
        self.jira.send_buffer()


    def run(self, cmd):
        results = self._run(cmd)
        if results.rc != 0:
            self.jira.add("Aquilon command failed")
            self.jira.add("Info from execution")
            self.jira.add(results.report_to_jira)
            self.jira.add("raising Exception")
            self.jira.send_buffer()
            raise HVException("aquilon command failed")
        return results

    def _run(self, cmd):
        self.client.connect(hostname="aquilon.gridpp.rl.ac.uk", username=self.creds_handler.aquilon.username, password=self.creds_handler.aquilon.password)
        aqcmd = "export AQHOST=aquilon.gridpp.rl.ac.uk; export AQSERVICE=aqd;"
        aqcmd += "export PATH=/opt/aquilon/bin/:$PATH;"
        aqcmd += "export PATH=/var/quattor/bin/:$PATH;"
        aqcmd += cmd
        stdin, stdout, stderr = self.client.exec_command(aqcmd)
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        rc = stdout.channel.recv_exit_status()
        self.client.close()
        results = Results(cmd, output, error, rc)
        return results



