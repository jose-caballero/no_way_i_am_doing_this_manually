import paramiko
import os
import re
from lib.hvexception import HVException
from lib.hvlocal import Results

class HVSSH:
    def __init__(self, hypervisormanager):
        """
        Helper for executing commands on the HyperVisor via SSH

        Parameters
        ----------
        hypervisormanager : HyperVisorManager
            Manager providing credentials, hostname and Jira helper.
        """
        self.creds_handler = hypervisormanager.creds_handler
        self.hostname = hypervisormanager.hostname
        self.ssh_private_key_path = self.creds_handler.ssh.key_path
        self.ssh_public_key_path = self.ssh_private_key_path + '.pub'
        self.ssh_username = self.creds_handler.ssh.username
        self.ssh_passphrase = self.creds_handler.ssh.passphrase
        self.jira = hypervisormanager.jira
        self.hvaquilon = hypervisormanager.hvaquilon
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.private_key = paramiko.RSAKey.from_private_key_file(self.ssh_private_key_path, password=self.ssh_passphrase)

    def is_rocky_8(self):
        """
        Check that the HyperVisor is running Rocky 8
        Raise an Exception if that is not the case
        """
        self.jira.add("Checking the OS is Rocky 8")
        results = self.run("cat /etc/os-release | grep VERSION_ID | awk -F= '{print $2}'", "root")
        self.jira.add(results.report_to_jira)
        version = results.stdout[1:-1] # only the number embedded inside double quotes
        if version.startswith('8'):
            msg = f"the hypervisor {self.hostname} is Rocky 8. Ready to start."
            self.jira.add(msg)
            self.jira.send_buffer()
        else:
            msg = f"the hypervisor {self.hostname} is not Rocky 8. Aborting"
            self.jira.add(msg)
            self.jira.send_buffer()
            raise HVException(msg)

    def is_rocky_9(self):
        """
        Check that the HyperVisor is running Rocky 9
        Raise an Exception if that is not the case
        """
        self.jira.add("Checking the OS is Rocky 9")
        results = self.run("cat /etc/os-release | grep VERSION_ID | awk -F= '{print $2}'", "root")
        self.jira.add(results.report_to_jira)
        version = results.stdout[1:-1] # only the number embedded inside double quotes
        if version.startswith('9'):
            msg = f"the hypervisor {self.hostname} is Rocky 9. Ready to continue."
            self.jira.add(msg)
            self.jira.send_buffer()
        else:
            msg = f"the hypervisor {self.hostname} is not Rocky 9. Aborting"
            self.jira.add(msg)
            self.jira.send_buffer()
            raise HVException(msg)


    @property
    def has_root_access(self):
        """
        check if the current local account has root access to the HyperVisor
        """
        try:
            self.client.connect(self.hostname, username="root", pkey=self.private_key, timeout=5)
            self.client.exec_command("true")  # Simple command to confirm access
            return True
        except Exception:
            return False

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

        Returns
        -------
        bool
            ``True`` if the hypervisor has no guests.
        Raises
        ------
        HVException
            If guests are present on the host.
        """
        self.jira.add("checking if HV is empty from within the host")
        results = self.run("virsh list --all", "root")
        self.jira.add(results.report_to_jira)
        out_l = results.stdout.split('\n')
        empty = (len(out_l) == 2)
        self.jira.add(f"is HV empty? {empty}")
        if empty:
            self.jira.send_buffer()
        if not empty:
            self.jira.add("Hypervisor still not empty. Raising an Exception")
            self.jira.send_buffer()
            raise HVException("hypervisor still not empty")

    def virsh_info(self)
        """
        Log information about the number of running VMs
        """
        self.jira.add("checking the number of running VMs")
        results = self.run("virsh list --all", "root")
        self.jira.add(results.report_to_jira)
        self.jira.send_buffer()

    def blocks_info(self):
        """
        Log information about block devices on the HyperVisor
        """
        self.jira.add("checking the block devices on the HV")
        results = self.run("lsblk", "root")
        self.jira.add(results.report_to_jira)
        self.jira.send_buffer()

    def gpus_info(self):
        """
        Log information about the detected NVIDIA GPUs on the HyperVisor
        """
        self.jira.add("checking the nvidia cards on the HV")
        results = self.run("lspci | grep -i nvidia", "root")
        self.jira.add(results.report_to_jira)
        self.jira.send_buffer()

    def mellanox_info(self):
        """
        return output from lspci for Mellanox devices
        """
        self.jira.add("checking the presence of mellanox cards on the HV")
        results = self.run("lspci | grep -i mellanox", "root")
        self.jira.add(results.report_to_jira)
        self.jira.send_buffer()
        return results.stdout
    
    def verify_is_efi(self):
        """
        Check whether the machine uses EFI firmware
        Raise an Exception when that is not the case
        """
        self.jira.add("checking if the HV is EFI")
        results = self.run("ls /sys/firmware/ | grep efi", "root")
        self.jira.add(results.report_to_jira)
        if results.stdout != "":
            self.jira.add("the hypervisor is EFI enabled")
            self.jira.send_buffer()
        else:
            self.jira.add("the hypervisor is not EFI enabled. Raising an Exception")
            self.jira.send_buffer()
            raise HVException("the hypervisor is not EFI enabled")


    def ensure_root_access(self):
        """
        copy ssh keys to root account on the hypervisor
        """
        self.jira.add("ensuring SSH as root to the hypervisor")
        if self.has_root_access:
            msg = f"user {self.ssh_username} already has root access to hypervisor {self.hostname}"
            self.jira.add(msg)
            self.jira.send_buffer()
            return
        # if not root access...
        msg = f"user {self.ssh_username} does not have yet root access to hypervisor {self.hostname}"
        self.jira.add(msg)

        # Read your public SSH key
        with open(self.ssh_public_key_path, "r") as pubkey_file:
            public_key = pubkey_file.read().strip()
        command = f"""
        sudo -S su -c 'grep -qF "{public_key}" /root/.ssh/authorized_keys || echo "{public_key}" >> /root/.ssh/authorized_keys'
        """
        results = self.run(command)
        self.jira.add(results.report_to_jira)
        msg = f"user {self.ssh_username} now has root access to hypervisor {self.hostname}"
        self.jira.add(msg)
        self.jira.send_buffer()

    def update_qemu_kvm(self):
        """
        Update qemu-kvm on the HV to apply some bug-fixes for draining VMs
        """
        self.jira.add("updating qemu")
        results = self.run('dnf -y update qemu-kvm', 'root')
        self.jira.add(results.report_to_jira)
        if results.rc != 0:
            self.jira.add("command failed. Checking the content of file /etc/resolv.conf")
            results_resolv = self.run('cat /etc/resolv.conf', 'root')
            self.jira.add(results_resolv.report_to_jira) 
        self.jira.send_buffer()
        if results.rc != 0:
            raise HVException("updating qemu failed")


    def hardware_specific(self):
        model = self.hvaquilon.model 
        if model == "hv-2022-lenovo":
            self._hardware_fix_2022_lenovo()
        if model == "xma-hv-2022-a100":
            self._hardware_fix_xma_hv_2022_a100()

    def _hardware_fix_2022_lenovo(self):
        self.jira.add("Performing hardware specific fixes for 2022 Lenovo HyperVisors")
        self.run('mkfs.xfs /dev/nvme0n1 -f', 'root')
        self.jira.add(results.report_to_jira)
        self.run('echo "/dev/nvme0n1 /var/lib/nova/instances xfs rw,relatime,attr2,inode64,logbufs=8,logbsize=32k,noquota" >> /etc/fstab', 'root')
        self.jira.add(results.report_to_jira)
        self.run('mkdir -p /var/lib/nova/instances', 'root')
        self.jira.add(results.report_to_jira)
        self.run('mount -a', 'root')
        results = self.run('lsblk', 'root')
        self.jira.add(results.report_to_jira)
        if "/var/lib/nova/instances" not in results.stdout:
            self.jira.add("New mount did not work as expected. Aborting")
            self.jira.add_block(results.stdout)
            self.jira.send_buffer()
            raise HVException("New mount did not work as expected. Aborting")
        self.run('systemctl daemon-reload', 'root')
        self.jira.add(results.report_to_jira)
        self.jira.send_buffer()

    def _hardware_fix_xma_hv_2022_a100(self):
        self.jira.add("Performing hardware specific fixes for 2022 XMA A100 HyperVisors")
        sel.run('mdadm --zero-superblock /dev/nvme0n1', 'root')
        self.jira.add(results.report_to_jira)
        sel.run('sgdisk -n 1:0:0 /dev/nvme0n1', 'root')
        self.jira.add(results.report_to_jira)
        sel.run('sgdisk -t 1:fd00 /dev/nvme0n1', 'root')
        self.jira.add(results.report_to_jira)
        sel.run('mdadm --create --verbose /dev/md0 --level=0 --raid-devices=2 /dev/nvme0n1p1 /dev/nvme1n1p1', 'root')
        self.jira.add(results.report_to_jira)
        sel.run('mkfs.xfs /dev/md0', 'root')
        self.jira.add(results.report_to_jira)
        sel.run('mdadm --detail --scan >> /etc/mdadm.conf', 'root')
        self.jira.add(results.report_to_jira)
        self.jira.send_buffer()
        

    # --------------------------------------------
    #   Generic execution methods
    # --------------------------------------------

    def run(self, cmd, username=None):
        results = self._run(cmd, username)
        if results.rc != 0:
            self.jira.add("Remote command failed")
            self.jira.add("Info from execution")
            self.jira.add(results.report_to_jira)
            self.jira.add("raising Exception")
            self.jira.send_buffer()
            raise HVException("Remote command failed")
        return results

    def _run(self, cmd, username=None):
        if not username:
            # if not username is passed, e.g. "root", 
            # we SSH as the regular user set in creds.yaml
            username = self.creds_handler.ssh.username
        self.client.connect(hostname=self.hostname, port=22, username=username, pkey=self.private_key)
        stdin, stdout, stderr = self.client.exec_command(cmd)
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        rc = stdout.channel.recv_exit_status()
        self.client.close()
        results = Results(cmd, output, error, rc)
        return results
