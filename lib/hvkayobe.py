import subprocess
from lib.hvexception import HVException
from lib.hvlocal import run

class HVKayobe:
    def __init__(self, hypervisormanager):
        """
        class to interact with the Kayobe Management host
        to deploy playbooks

        Parameters
        ----------
        hypervisormanager : HyperVisorManager
            Manager instance providing credentials and Jira reporting.
        """
        self.creds_handler = hypervisormanager.creds_handler
        self.jira = hypervisormanager.jira
        self.hostname = hypervisormanager.hostname

    def run_mellanox_playbook(self):
        """
        Execute a bash script on the Kayobe host to run the mellanox playbook
        """
        self.jira.add("Running the Mellanox playbook on the Kayobe host")
        self.jira.send_buffer()
        cmd = f"~/no_way_i_am_doing_this_manually/scripts/mellanox_playbook.sh {self.hostname}"
        self.run(cmd)

    def run_cleanup_tmp(self):
        """
        remove the files under /tmp/
        """
        cmd = "~/cleanup_tmp.sh"
        self.run(cmd)

    def run_inventory_from_netbox(self):
        """
        Execute a wrapper bash script on the Kayobe host to synchronise
        inventory information from netbox
        """
        self.jira.add("updating inventory from netbox on Kayobe host")
        cmd = f"~/no_way_i_am_doing_this_manually/scripts/inventory_from_netbox.sh {self.hostname}"
        results = self.run(cmd)
        self.jira.add(results.report_to_jira)
        if "fatal" in results.stdout:
            self.jira.add("playbook failed, raising Exception")
            self.jira.send_buffer()
            raise HVException("playbook failed")
        else:
            self.jira.send_buffer()

    def run_kayobe_overcloud_host_configure(self):
        """
        Execute a wrapper bash script on the Kayobe host to 
        run the overcloud host configure playbooks
        """
        self.jira.add("executing kayobe overcloud host configure on Kayobe host")
        cmd = f"~/no_way_i_am_doing_this_manually/scripts/kayobe_overcloud_host_configure.sh {self.hostname}"
        results = self.run(cmd)
        self.jira.add(results.report_to_jira)
        if "fatal" in results.stdout:
            self.jira.add("playbook failed, raising Exception")
            self.jira.send_buffer()
            raise HVException("playbook failed")
        else:
            self.jira.send_buffer()

    def run_kayobe_overcloud_deploy_hypervisor(self):
        """
        Execute a wrapper bash script on the Kayobe host to 
        run the overcloud deploy hypervisor playbooks
        """
        self.jira.add("executing kayobe overcloud deploy hypervisor on Kayobe host")
        cmd = f"~/no_way_i_am_doing_this_manually/scripts/kayobe_overcloud_deploy_hypervisor.sh {self.hostname}"
        results = self.run(cmd)
        self.jira.add(results.report_to_jira)
        if "fatal" in results.stdout:
            self.jira.add("playbook failed, raising Exception")
            self.jira.send_buffer()
            raise HVException("playbook failed")
        else:
            self.jira.send_buffer()

    def run_kayobe_overcloud_deploy_controller(self):
        """
        Execute a wrapper bash script on the Kayobe host to 
        run the overcloud deploy controller playbooks
        """
        self.jira.add("executing kayobe overcloud deploy controller on Kayobe host")
        cmd = f"~/no_way_i_am_doing_this_manually/scripts/kayobe_overcloud_deploy_controller.sh {self.hostname}"
        results = self.run(cmd)
        self.jira.add(results.report_to_jira)
        if "fatal" in results.stdout:
            self.jira.add("playbook failed, raising Exception")
            self.jira.send_buffer()
            raise HVException("playbook failed")
        else:
            self.jira.send_buffer()


    def run(self, cmd):
        """
        execute any arbitrary command on the Kayobe host
        and handle errors
        """
        try:
            self._run(cmd)
        except HVException as ex:
            self.jira.add("The remote kayobe failed. Aborting.")
            self.jira.send_buffer()
            raise ex
        except Exception as ex:
            msg = f'Exception captured: {ex}'
            self.jira.add("Exception captured")
            self.jira.add_block(ex)
            self.jira.send_buffer()
            raise ex

    def _run(self, cmd):
        """
        Run a command on the Kayobe host via SSH.
        Ensure the SSH key are being propogated to the host.

        Parameters
        ----------
        cmd : str
            Command line to execute remotely.
        Returns
        -------
        Results
            Execution results from :func:`hvlocal.run`.
        """
        full_cmd = (
            "eval $(ssh-agent) >/dev/null; "
            f"ssh-add {self.creds_handler.kayobe.nopassfile} &>/dev/null; "
            f"ssh -A {self.creds_handler.kayobe.username}@{self.creds_handler.kayobe.hostname} '{cmd}'"
        )
        results = run(full_cmd)
        results.cmd = cmd # we remove local information from the cmd line, for security purposes
        self.jira.add(results.report_to_jira)
        self.jira.send_buffer()
        if results.rc != 0:
            raise HVException("kayobe command failed")

