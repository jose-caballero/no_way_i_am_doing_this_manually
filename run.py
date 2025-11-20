import argparse
import sys
import textwrap

from lib.migrationmanager import MigrationManager


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Script to perform actions with given hypervisors and credentials.", 
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--hypervisors-file',
        default='etc/hypervisors.txt',
        help='Path to the hypervisors file (default: etc/hypervisors.txt)'
    )
    parser.add_argument(
        '--creds-file',
        default='etc/creds.yaml',
        help='Path to the credentials file (default: etc/creds.yaml)'
    )
    parser.add_argument(
        '--step',
        required=True,
        choices=['setup', 'pre_drain', 'pre_reinstall', 'post_reinstall', 'noops'],
        help=textwrap.dedent("""\
            Specify the step to run

            setup:
               adds your public SSH key to the hypervisor to grant access as root

            pre_drain:
               verifies the hypervisor is still Rocky 8
               updates the RPM for qemu
               verifies the hypervisor is listed in Netbox
               checks the status of the hypervisor in Netbox
               disables the hypervisor from OpenStack
               lists the VMs currently running on the hypervisor

            pre_reinstall:
                ensures the hypervisor is not hosting any VM
                lists block devices
                gets GPUs info
                creates silences in AlertManager
                changes the status of the hypervisor in Netbox to "planned"
                executes script "re-import" in the Aquilon host 
                executes script "remove_interfaces.py" in the Aquilon host to remove unnecessary interfaces
                executes script "remove_sata_disk.py" in the Aquilon host to remove unnecessary disks
                executes script "make_host.py" to recompile the hypervisor in Aquilon with the right Domain, Personality and OS info
                executes script "pxeswitch_host.py" to pxeswitch the hypervisor in Aquilon
                gets mellanox info from the hypervisor and run ansible playbook if needed
                gets the IPMI address

            post_reinstall:
                ensures the hypervisor is now on Rocky 9
                lists block devices
                gets GPU info
                checks if the hypervisor is not efi-like
                changes the status in Netbox to "active" and the role to "Openstack Prod Kolla_Compute"

            noops:
                this step does not anything 

        """)
    )
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    manager = MigrationManager(args.creds_file, args.hypervisors_file)
    manager.run(args.step)
