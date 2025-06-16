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

    @property
    def is_rocky_8(self):
        out, err, rc = self.run("cat /etc/os-release | grep VERSION_ID | awk -F\= '{print $2}'")
        _,version,_ = out.split('"')
        return version.startswith('8')

    @property
    def has_root_access(self):
        try:
            self.client.connect(self.hostname, username="root", pkey=self.private_key, timeout=5)
            self.client.exec_command("true")  # Simple command to confirm access
            return True
        except Exception:
            return False

    @property
    def is_empty(self):
        """
        check if the ouptut of command "virsh list --all" is empty. 
        Normally, it looks like this

        [root@hv624 ~]# virsh list --all
        Id    Name                State
        -----------------------------------
        14    instance-00998525   running
        16    instance-0099852b   running
        17    instance-0099852e   running
        33    instance-00998591   running
        35    instance-00998597   running
        36    instance-0099859d   running
        37    instance-009985a6   running
        40    instance-009985be   running
        60    instance-009987f5   running
        63    instance-009988e2   running
        72    instance-009992d5   running
        78    instance-00999320   running
        82    instance-00999347   running
        113   instance-00999947   running
        116   instance-0099996e   running

        It looks like this when empty

        [root@hv624 ~]# virsh list --all
        Id    Name                State
        -----------------------------------
        """
        out, err, rc = self.run("virsh list --all", "root")
        self.log.debug("checking if HV is empty")
        self.log.debug(out)
        self.jira.add("checking if HV is empty")
        self.jira.add("executing command 'virsh list --all'")
        self.jira.add_block(out)
        out_l = out.split('\n')
        empty = (len(out_l) == 2)
        self.jira.add(f"is HV empty? {empty}")
        self.jira.send_buffer()
        return emtpy

    def blocks_info(self):
        out, err, rc = self.run("lsblk", "root")
        self.log.debug(out)
        self.jira.add("checking the block devices on the HV")
        self.jira.add("executing command 'lsblk'")
        self.jira.add_block(out)
        self.jira.send_buffer()

    def gpus_info(self):
        out, err, rc = self.run("lspci | grep -i nvidia", "root")
        self.log.debug(out)
        self.jira.add("checking the nvidia cards on the HV")
        self.jira.add("executing command 'lspci'")
        self.jira.add_block(out)
        self.jira.send_buffer()

    @property
    def mellanox_info(self):
        out, err, rc = self.run("lspci | grep -i mellanox", "root")
        self.log.debug(out)
        self.jira.add("checking the presence of mellanox cards on the HV")
        self.jira.add("executing command 'lspci | grep -i mellanox'")
        self.jira.add_block(out)
        self.jira.send_buffer()
        return out

    @property
    def is_efi(self):
        out, err, rc = self.run("ls /sys/firmware/ | grep efi", "root")
        return out != ""

    def ensure_root_access(self):
        """
        copy ssh keys to root account on the hypervisor
        """
        if self.has_root_access:
            msg = f"user {self.ssh_username} already has root acccess to hypervisor {self.hostname}"
            self.log.debug(msg)
            self.jira.add(msg)
            self.jira.send_buffer()
            return

        # if not root access...
        msg = f"user {self.ssh_username} does not have yet root acccess to hypervisor {self.hostname}"
        self.log.debug(msg)
        self.jira.add(msg)
        self.jira.send_buffer()

        # Connect as regular user
        self.client.connect(self.hostname, username=self.ssh_username, pkey=self.private_key)
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
        self.client.close()

        msg = f"user {self.ssh_username} now has root acccess to hypervisor {self.hostname}"
        self.log.debug(msg)
        self.jira.add(msg)
        self.jira.send_buffer()

    def update_qemu_kvm(self):
        """
        Update qemu-kvm on the HV to apply some bug-fixes for draining VMs
        """
        out, err, rc = self.run('dnf update qemu-kvm', 'root')
        self.jira.add("updating qemu-kvm")
        self.jira.add("executing command: 'dnf update qemu-kvm'")
        self.jira.add_block(out)
        self.jira.send_buffer()


    # --------------------------------------------
    #   Generic execution methods
    # --------------------------------------------

    def run(self, cmd, username=None):
        try:
            self.log.debug('starting run')
            out, err, rc = self._run(cmd, username)
            self.log.debug('leaving run')
            return out, err, rc
        except Exception as ex:
            msg = f'Exception captured: {ex}'
            self.log.debug(msg)
            self.jira.add("Exception captured")
            self.jira.add_block(ex)
            self.jira.send_buffer()
            raise ex
        
    def _run(self, cmd, username=None):
        if not username:
            # if not username is passed, e.g. "root", 
            # we SSH as the regular user set in creds.yaml
            username = self.creds_handler.ssh.username
        self.client.connect(hostname=self.hostname, port=22, username=self.ssh_username, pkey=self.private_key)
        stdin, stdout, stderr = self.client.exec_command(cmd)
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        rc = stdout.channel.recv_exit_status()
        self.client.close()
        return output, error, rc
