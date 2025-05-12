import argparse
import sys

from migrationmanager import MigrationManager


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Script to perform actions with given hypervisors and credentials."
    )
    parser.add_argument(
        '--hypervisors-file',
        default='hypervisors.txt',
        help='Path to the hypervisors file (default: hypervisors.txt)'
    )
    parser.add_argument(
        '--creds-file',
        default='creds.yaml',
        help='Path to the credentials file (default: creds.yaml)'
    )
    parser.add_argument(
        '--step',
        required=True,
        choices=['setup', 'pre-bios', 'post-bios', 'finish'],
        help='Specify the step to run: setup, pre-bios, post-bios, or finish'
    )
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    manager = MigrationManager(args.creds_file, args.hypervisors_file)
    manager.run(args.step)
