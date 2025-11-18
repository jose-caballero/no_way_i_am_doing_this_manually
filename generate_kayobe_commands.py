"""
Generate command strings from a list of hostnames in a file.

Usage:
    python generate_commands.py               # uses default 'hypervisors.txt'
    python generate_commands.py /path/to/file
"""

import argparse      # Module to handle command-line arguments
import sys           # Module for system functions
from pathlib import Path  # Filesystem path handling


def parse_args():
    """Parse command-line arguments and return them."""
    parser = argparse.ArgumentParser(
        description="Generate ansible and kayobe commands from a hostname list file."
    )
    # Add an optional positional argument; if omitted, uses the default file
    parser.add_argument(
        "input_file",
        nargs="?",                     # Makes the argument optional
        default="etc/hypervisors.txt",     # Default file path
        help="Path to input file (default: hypervisors.txt)",
    )
    return parser.parse_args()


def read_hostnames(file_path):
    """
    Read hostnames from a file.

    - Only the first whitespace-separated column per non-empty line is used.
    - Lines starting with '#' are ignored.
    """
    path = Path(file_path)

    # Ensure the file exists
    if not path.is_file():
        print(f"Error: '{file_path}' is not a valid file.", file=sys.stderr)
        sys.exit(1)

    hostnames = []

    # Open file and read lines
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()     # Remove whitespace around line

            if not stripped:
                continue               # Skip empty lines

            if stripped.startswith("#"):
                continue               # Skip comments

            parts = stripped.split()   # Split into whitespace columns
            if parts:
                hostnames.append(parts[0])  # Store the first column (hostname)

    return hostnames


def build_commands(hostnames):
    """Build the three required command strings."""
    inventory_hosts = ",".join(hostnames)
    inventory_hosts_with_trailing_comma = inventory_hosts + ","
    colon_hosts = ":".join(hostnames)

    cmd1 = (
        "ansible-playbook ansible/mellanox-enable-uefi-pxe.yml "
        f"-i {inventory_hosts_with_trailing_comma} "
        f'--extra-vars "pxe_target={colon_hosts}"'
    )

    cmd2 = (
        "kayobe overcloud host configure "
        "-e selinux_do_reboot=true "
        f"-kl {colon_hosts} "
        f"--limit {colon_hosts}"
    )

    cmd3 = (
        "kayobe overcloud service deploy "
        f"-kl {colon_hosts} "
        f"--limit {colon_hosts}"
    )

    return [cmd1, cmd2, cmd3]


def main():
    """Main execution flow."""
    args = parse_args()
    hostnames = read_hostnames(args.input_file)

    if not hostnames:
        print(
            f"No hostnames found in file '{args.input_file}'.",
            file=sys.stderr,
        )
        sys.exit(1)

    commands = build_commands(hostnames)

    print()
    for cmd in commands:
        print(cmd)
        print()


if __name__ == "__main__":
    main()

