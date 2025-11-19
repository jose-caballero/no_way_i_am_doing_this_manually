# Project Architecture

This repository provides automation scripts and helper classes for migrating hypervisors to Rocky 9. The code is organised as a collection of Python modules that interact with several external services (Jira, NetBox, OpenStack, Aquilon, Alertmanager and SSH) together with a set of shell helper scripts.

## Overview

The main entry point is `run.py`. It parses command line arguments, creates a `MigrationManager` and invokes the selected migration step. A migration step corresponds to one of the phases of the hypervisor migration process:
* setup
* pre-drain
* drain
* pre-reinstall
* post-reinstall
* adoption
* noops


### Credentials

Credentials for all services are loaded from a YAML file through `CredentialsHandler` (see `credentialshandler.py`). It defines several dataclasses (for OpenStack, Jira, Alertmanager, NetBox, SSH, Aquilon and Kayobe) and exposes them as attributes so that all modules use a single source of credentials.

### MigrationManager

`MigrationManager` (in `migrationmanager.py`) is responsible for:

* Reading the list of hypervisors and their associated Jira ticket IDs from a text file.
* Setting up logging (logs are written to `./logs/<hypervisors_file>.<timestamp>`).
* Creating a `HyperVisorManager` instance for each hypervisor and executing the desired step either sequentially or in parallel.
* Providing a `TimeInterval` object which represents the start and end time window used when interacting with Alertmanager and other services.

### HyperVisorGroup

The class `HyperVisorGroup` (in `hypervisorgroup.py`) is a simple container with a list of `HyperVisorManager` objects, one for each Hypervisor being migrated. Its main responsibility is to call the method `run()` either in series or in parallel for each one of them.

### HyperVisorManager

`HyperVisorManager` (in `hypervisormanager.py`) orchestrates operations for a single hypervisor. During initialisation it creates helper objects for each external service:

* `HVJira` – interacts with Jira, adds comments and moves issues between states.
* `HVAlertManager` – creates silences in Alertmanager during maintenance windows.
* `HVNetbox` – queries and updates NetBox device information.
* `HVOpenstack` – communicates with the OpenStack API to manage compute services and list servers.
* `HVAquilon` – runs commands on the Aquilon host via SSH.
* `HVSSH` – connects directly to the hypervisor host via SSH to execute commands.
* `HVKayobe` – runs Kayobe playbooks on a dedicated Kayobe host.
* `HVLocal` – runs OpenStack CLI commands on the local machine.

Each migration step, e.g. `_run_setup()` or `_run_pre_drain()`, makes calls to these helpers to perform the required actions and logs progress both locally and to Jira.

### Service Helpers

Each helper encapsulates the logic to interact with an external system. Notable examples include:

* `hvssh.py` – uses Paramiko to execute commands on the hypervisor. It can ensure root access, inspect hardware, apply hardware fixes and update packages.
* `hvnetbox.py` – uses the NetBox API (via `pynetbox`) to query status, change roles or retrieve IPMI addresses.
* `hvopenstack.py` – utilises the OpenStack SDK to disable the compute service and list virtual machines hosted on the hypervisor.
* `hvalertmanager.py` – communicates with Alertmanager’s HTTP API to create silences for the maintenance window defined by `TimeInterval`.
* `hvjira.py` – wraps the Jira client, providing methods to append comments and transition issues between workflow states.
* `hvkayobe.py` – executes shell scripts on the Kayobe host to run Ansible playbooks for configuring hardware or deploying services.
* `hvlocal.py` – executes local OpenStack CLI commands, for example to disable or enable a hypervisor.
* `hvaquilon.py` – runs Aquilon commands on a remote host over SSH to manipulate host definitions.

Logging for these helpers is unified via `logger.SetLogger`, which dynamically attaches a logger derived from the calling `HyperVisorManager` instance.

### Helper Scripts

The `scripts/` directory contains scripts that are executed on remote hosts:
* a host with a Kayobe environment
* the Aquilon host

They wrap Kayobe or Aquilon operations such as building inventory from NetBox, deploying services, or re-importing hosts.
In the case of the Kayobe scripts, they record the output in a file, and only return the relevant lines from it. 
In the case of the Aquilon scripts, they may use `myaq` library. 


### Additional Utilities

* `create_jira_tickets.py` – script that creates Jira issues for each hypervisor listed in the input file.
* `generate_kayobe_commands.py` - script to generate some of the commands to be used in the host with a Kayobe environment, to avoid typos and other mistakes.

## Data Flow

1. **Execution Start** – The user runs `python run.py --step <step>` specifying the credentials file and hypervisor list.
2. **Initialisation** – `MigrationManager` loads credentials, parses the hypervisor file and prepares logging.
3. **Step Execution** – For each hypervisor, a `HyperVisorManager` is created. Depending on the chosen step it invokes a series of actions via the service helpers. Results and errors are logged locally and as comments on the corresponding Jira issue.

## Directory Layout

```
.
├── README.md
├── ARCHITECTURE.md
├── run.py
├── create_jira_tickets.py
├── generate_kayobe_commands.py
├── etc
│   ├── creds.yaml.template
│   └── hypervisors.txt.template
├── lib
│   ├── credentialshandler.py
│   ├── hvalertmanager.py
│   ├── hvaquilon.py
│   ├── hvexception.py
│   ├── hvjira.py
│   ├── hvkayobe.py
│   ├── hvlocal.py
│   ├── hvnetbox.py
│   ├── hvopenstack.py
│   ├── hvssh.py
│   ├── hypervisorgroup.py
│   ├── hypervisormanager.py
│   ├── migrationmanager.py
│   └── timeinterval.py
└── scripts
    ├── cleanup_tmp.sh
    ├── inventory_from_netbox.sh
    ├── kayobe_overcloud_deploy_controller.sh
    ├── kayobe_overcloud_deploy_hypervisor.sh
    ├── kayobe_overcloud_host_configure.sh
    ├── make_host.py
    ├── manage_hv_to_sandbox.py
    ├── mellanox_playbook.sh
    ├── parse_logfile.sh
    ├── prepare_host.py
    ├── pxeswitch_host.py
    ├── reimport-host.sh
    ├── remove_interfaces.py
    └── remove_sata_disk.py
```

