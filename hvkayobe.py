import subprocess
from hvexception import HVException
from hvlocal import run

class HVKayobe:
    def __init__(self, hypervisormanager):
        self.creds_handler = hypervisormanager.creds_handler
        self.jira = hypervisormanager.jira
        self.hostname = hypervisormanager.request.hypervisor

    def run_mellanox_playbook(self):
        self.jira.add("Running the Mellanox playbook on the Kayobe host")
        self.jira.send_buffer()
        cmd = f"~/mellanox_playbook.sh {self.hostname}"
        self.run(cmd)

    def run_cleanup_tmp(self):
        cmd = "~/cleanup_tmp.sh"
        self.run(cmd)

    def run_inventory_from_netbox(self):
        self.jira.add("updating inventory from netbox on Kayobe host")
        cmd = f"~/inventory_from_netbox.sh {self.hostname}"
        results = self.run(cmd)
        self.jira.add(results.report_to_jira)
        if "fatal" in results.stdout:
            self.jira.add("playbook failed, raising Exception")
            self.jira.send_buffer()
            raise HVException("playbook failed")
        else:
            self.jira.send_buffer()

    def run_kayobe_overcloud_host_configure(self):
        self.jira.add("executing kayobe overcloud host configure on Kayobe host")
        cmd = f"~/kayobe_overcloud_host_configure.sh {self.hostname}"
        results = self.run(cmd)
        self.jira.add(results.report_to_jira)
        if "fatal" in results.stdout:
            self.jira.add("playbook failed, raising Exception")
            self.jira.send_buffer()
            raise HVException("playbook failed")
        else:
            self.jira.send_buffer()

    def run_kayobe_overcloud_deploy_hypervisor(self):
        self.jira.add("executing kayobe overcloud deploy hypervisor on Kayobe host")
        cmd = f"~/kayobe_overcloud_deploy_hypervisor.sh {self.hostname}"
        results = self.run(cmd)
        self.jira.add(results.report_to_jira)
        if "fatal" in results.stdout:
            self.jira.add("playbook failed, raising Exception")
            self.jira.send_buffer()
            raise HVException("playbook failed")
        else:
            self.jira.send_buffer()

    def run_kayobe_overcloud_deploy_controller(self):
        self.jira.add("executing kayobe overcloud deploy controller on Kayobe host")
        cmd = f"~/kayobe_overcloud_deploy_controller.sh {self.hostname}"
        results = self.run(cmd)
        self.jira.add(results.report_to_jira)
        if "fatal" in results.stdout:
            self.jira.add("playbook failed, raising Exception")
            self.jira.send_buffer()
            raise HVException("playbook failed")
        else:
            self.jira.send_buffer()


    def run(self, cmd):
        try:
            self._run(cmd)
        except Exception as ex:
            msg = f'Exception captured: {ex}'
            self.jira.add("Exception captured")
            self.jira.add_block(ex)
            self.jira.send_buffer()
            raise ex

    def _run(self, cmd):
        """
        arguments for the remote command:
             command to execute
        """
        cmd = (
            "eval $(ssh-agent) >/dev/null; "
            f"ssh-add {self.creds_handler.kayobe.nopassfile} &>/dev/null; "
            f"ssh -A {self.creds_handler.kayobe.username}@{self.creds_handler.kayobe.hostname} '{cmd}'"
        )
        results = run(cmd)
        return results

