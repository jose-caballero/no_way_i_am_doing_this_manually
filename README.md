# Library to automate the migration of Hypervisors to Rocky 9

---

## Dependencies

If not yet installed, the following packages are required:

- `paramiko`
- `openstacksdk`
- `jira`
- `pynetbox`

You can install them using pip:

```bash
pip install paramiko
pip install openstacksdk
pip install jira 
pip install pynetbox
```

---

## Set working environment

### Get the code

```bash
git clone https://github.com/jose-caballero/no_way_i_am_doing_this_manually.git
cd no_way_i_am_doing_this_manually/
```

### Set the credentials 

```bash
cd etc/
cp creds.yaml.template creds.yaml
vi creds.yaml
```

Edit the `creds.yaml` file and add your secrets.  
Ask around to get the credentials for services like Icinga, Alertmanager, etc.

### Set the list of hostnames

```bash
cd etc/
cp hypervisors.txt.template hypervisors.txt
vi hypervisors.txt
```

Edit the `hypervisors.txt` file with the list of HVs you want to migrate.
One hostname per line. 

If no JIRA tickets have been created yet for the list of HVs being migrated, just add the hostnames and create the JIRA tickets with script `create_jira_tickets.py`. 
This script will create one JIRA ticket for each hostname in the file, and it will add the ticket ID to the file. 

If the JIRA tickets already exist, add them to the file like this:

```
<hosname 1> <ticket ID 1>
<hosname 2> <ticket ID 2>
...
<hosname N> <ticket ID N>
```


### Copy scripts to remote hosts

* copy the following scripts to a host with the Kayobe environment, underneath `hv_migration_scripts/` in your home directory:
   * cleanup_tmp.sh
   * inventory_from_netbox.sh
   * kayobe_overcloud_deploy_controller.sh
   * kayobe_overcloud_deploy_hypervisor.sh
   * kayobe_overcloud_host_configure.sh
   * mellanox_playbook.sh
   * parse_logfile.sh

* copy the following scripts to your account in the Aquilon host:
   * make_host.py
   * manage_hv_to_sandbox.py
   * prepare_host.py
   * pxeswitch_host.py
   * reimport-host.sh
   * remove_interfaces.py
   * remove_sata_disk.py


## Execution 

To see the options, just run:

```bash
python ./run.py --help
```

Or use `python3` depending on your environment.

Examples:

```bash
python ./run.py --help
python ./run.py --step pre-reinstall
python ./run.py --step pre-reinstall --creds-file /path/to/my/creds.yaml
```

