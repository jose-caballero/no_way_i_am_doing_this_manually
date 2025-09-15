import paramiko
from hvexception import HVException
from hvlocal import Results

class HVAquilon:
    def __init__(self, hypervisormanager):
        """
        class with utilities to interact with Aquilon
        initialises with credentials from hypervisormanager object

        param hypervisormanager: HyperVisorManager
        """
        self.creds_handler = hypervisormanager.creds_handler
        self.jira = hypervisormanager.jira
        self.hostname = hypervisormanager.request.hypervisor
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    @property
    def model(self):
        """
        return the hardware model reported by Aquilon
        """
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
        """
        execute a bash script on the Aquilon host to reimport the 
        HyperVisor definition
        """
        self.jira.add("Executing script to re-import the host on Aquilon")
        cmd = f"./reimport-host.sh {self.hostname}"
        results = self.run(cmd)
        self.jira.add(results.report_to_jira)
        self.jira.send_buffer()
        

    def manage_to_sandbox(self):
        """
        managed the HyperVisor into the development Sandbox
        """
        self.jira.add("Manage the host to David's Sandbox on Aquilon")
        cmd = f"python3 ./manage_hv_to_sandbox.py {self.hostname}"
        results = self.run(cmd)
        self.jira.add(results.report_to_jira)
        self.jira.send_buffer()

    def prepare_host(self):
        """
        executes a python script on the Aquilon to perform all 
        necessary steps to get the HyperVisor ready for re-install
        """
        self.jira.add("Recompiling and pxe switching the HV on Aquilon")
        cmd = f"python3 ./prepare_host.py {self.hostname}"
        results = self.run(cmd)
        self.jira.add(results.report_to_jira)
        self.jira.send_buffer()


    def run(self, cmd):
        """
        execute any arbitrary command on the Aquilon host
        """
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
        """
        do the actual execution of any arbitrary command on the Aquilon host
        fix the environment first
        """
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



