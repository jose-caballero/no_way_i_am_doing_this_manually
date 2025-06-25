# Project Architecture

This repository provides automation scripts and helper classes for migrating hypervisors to Rocky 9. The code is organised as a collection of Python modules that interact with several external services (Jira, NetBox, OpenStack, Aquilon, Alertmanager and SSH) together with a set of shell helper scripts.

## Overview

The main entry point is `run.py`. It parses command line arguments, creates a `MigrationManager` and invokes the selected migration step. A migration step corresponds to one of the phases of the hypervisor migration process (`setup`, `pre-drain`, `pre-reinstall`, `post-reinstall`, `adoption` or `noops`).

```
run.py -> MigrationManager -> HyperVisorManager -> [service helpers]
```

### Credentials

Credentials for all services are loaded from a YAML file through `CredentialsHandler` (see `credentialshandler.py`). It defines several dataclasses (for OpenStack, Jira, Alertmanager, NetBox, SSH, Aquilon and Kayobe) and exposes them as attributes so that all modules use a single source of credentials.

### MigrationManager

`MigrationManager` (in `migrationmanager.py`) is responsible for:

* Reading the list of hypervisors and their associated Jira ticket IDs from a text file.
* Setting up logging (logs are written to `./logs/<hypervisors_file>.<timestamp>`).
* Creating a `HyperVisorManager` instance for each hypervisor and executing the desired step either sequentially or in parallel.
* Providing a `TimeInterval` object which represents the start and end time window used when interacting with Alertmanager and other services.

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

Each migration step (`_run_setup`, `_run_pre_drain`, `_run_pre_reinstall`, `_run_post_reinstall`, `_run_adoption` and `_run_noops`) makes calls to these helpers to perform the required actions and logs progress both locally and to Jira.

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

The `scripts/` directory contains shell scripts that are executed by `HVKayobe` or manually. They wrap Kayobe or Aquilon operations such as building inventory from NetBox, deploying services, or re-importing hosts.

### Additional Utilities

* `create_jira_tickets.py` – utility script that creates Jira issues for each hypervisor listed in the input file.
* `timeinterval.py` – calculates a start and end timestamp (four weeks apart) ensuring the end falls on a weekday; used for Alertmanager silences and OpenStack disable reasons.
* `hvexception.py` – simple custom exception class.

## Data Flow

1. **Execution Start** – The user runs `python run.py --step <step>` specifying the credentials file and hypervisor list.
2. **Initialisation** – `MigrationManager` loads credentials, parses the hypervisor file and prepares logging.
3. **Step Execution** – For each hypervisor, a `HyperVisorManager` is created. Depending on the chosen step it invokes a series of actions via the service helpers. Results and errors are logged locally and as comments on the corresponding Jira issue.
4. **Parallel Mode** – When `--parallel` is specified, each hypervisor is processed in its own thread.

## Directory Layout

```
.
├── run.py                    # CLI entry point
├── migrationmanager.py       # Manages workflow across hypervisors
├── hypervisormanager.py      # Orchestrates actions for one hypervisor
├── credentialshandler.py     # Loads credentials from YAML
├── hvssh.py                  # SSH operations on hypervisors
├── hvjira.py                 # Jira integration
├── hvalertmanager.py         # Alertmanager integration
├── hvnetbox.py               # NetBox integration
├── hvopenstack.py            # OpenStack integration
├── hvkayobe.py               # Kayobe host interactions
├── hvaquilon.py              # Aquilon host interactions
├── hvlocal.py                # Local OpenStack CLI helper
├── timeinterval.py           # Time window utilities
├── logger.py                 # Dynamic logger helper
├── create_jira_tickets.py    # Utility to create Jira issues
├── scripts/                  # Shell scripts invoked by helpers
└── README.md                 # Basic usage instructions
```

