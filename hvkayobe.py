import subprocess
import datetime

from logger import SetLogger

class HVKayobe(SetLogger):
    def __init__(self, hypervisormanager):
        self._set_logger()
        self.creds_handler = hypervisormanager.creds_handler
        self.jira = hypervisormanager.jira
        self.hostname = hypervisormanager.request.hypervisor

###    def setup_deployment_environment(self):
###        msg = "re running beokay on the Kayobe environment host to fetch latest packages and commits"
###        self.log.debug(msg)
###        self.jira.add_commen(msg)
###        self.run(
###            "python ./beokay.py create "
###            "--no-bootstrap "
###            f"--base-path ./{self.creds_handler.kayobe.prod_env_path} "
###            "--kayobe-repo git@gitlab.stfc.ac.uk:stfc-cloud/kayobe.git "
###            "--kayobe-branch scientific-openstack/yoga-stfc "
###            "--kayobe-config-repo git@gitlab.stfc.ac.uk:stfc-cloud/stfc-cloud-kayobe.git "
###            "--kayobe-config-branch stfc/yoga "
###            "--kayobe-config-env-name stfc-production "
###            "--vault-password-file ~/.productionvaultpassword"
###        )
###        self.run(
###            f"source ./{self.creds_handler.kayobe.prod_env_path}/env-vars.sh; "
###            "kayobe playbook run ansible/load-ssh-key.yml; "
###            "kayobe control host bootstrap"
###        )


    def run_mellanox_playbook(self):
        cmd = f"~/mellanox_playbook.sh {self.hostname}"
        self.run(cmd)

    def run_inventory_from_netbox(self):
        cmd = f"~/inventory_from_netbox.sh {self.hostname}"
        self.run(cmd)

    def run_kayobe_overcloud_host_configure(self):
        cmd = f"~/kayobe_overcloud_host_configure.sh {self.hostname}"
        self.run(cmd)

    def run_kayobe_overcloud_deploy_hypervisor(self):
        cmd = f"~/kayobe_overcloud_deploy_hypervisor.sh {self.hostname}"
        self.run(cmd)

    def run_kayobe_overcloud_deploy_controller(self):
        cmd = f"~/kayobe_overcloud_deploy_controller.sh {self.hostname}"
        self.run(cmd)


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
        """
        arguments for the remote command:
             command to execute
        """
        cmd = (
            "eval $(ssh-agent) >/dev/null; "
            f"ssh-add {self.creds_handler.kayobe.nopassfile} &>/dev/null; "
            f"ssh -A {self.creds_handler.kayobe.username}@{self.creds_handler.kayobe.hostname} '{cmd}'"
        )
        subproc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True)
        (out, err) = subproc.communicate()
        st = subproc.returncode
        self.log.debug(f'cmd = {cmd}')
        self.log.debug(f'output = {out}')
        self.log.debug(f'err = {err}')
        self.log.debug(f'rc = {st}')
        self.jira.add_comment("command:")
        self.jira.add_block(cmd)
        self.jira.add_comment("output:")
        self.jira.add_block(out)
        self.jira.add_comment("error:")
        self.jira.add_block(err)
        self.jira.add_comment("return code:")
        self.jira.add_block(st)
        # check if the output is OK
        if "fatal" in out:
            raise Exception("playbook failed")
