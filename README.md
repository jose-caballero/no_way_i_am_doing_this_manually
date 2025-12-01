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

You will also an account for the following services:

- JIRA
- Netbox
- AlertManager
- OpenStack
- Aquilon
- a host with kayobe environment

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
python ./run.py --step pre_reinstall
python ./run.py --step pre_reinstall --creds-file /path/to/my/creds.yaml
```

## ancillaries

### script to create the JIRA tickets

The JIRA tickets can be created easily with a script included in this repository. 

1. Follow the steps above to get the code and setup your working environment
2. Add the hostnames to a file, one per row, like this

```bash
$ cat hypervisors.txt
hv-rtx4000-26.nubes.rl.ac.uk
hv-rtx4000-04.nubes.rl.ac.uk
hv-rtx4000-32.nubes.rl.ac.uk
``` 
3. Execute the script
```bash
python ./create_jira_tickets.py
```
4. if everything went fine, the file with hypervisor names should now contain the Jira ticket IDs
```bash
$ cat hypervisors.txt
hv-rtx4000-26.nubes.rl.ac.uk MH-182
hv-rtx4000-04.nubes.rl.ac.uk MH-183
hv-rtx4000-32.nubes.rl.ac.uk MH-186
```

### script to generate the kayobe commands

To avoid typos, you can generate some of the commands to be executed on the kayobe enviroment with this script:

```bash
$ cat etc/hypervisors.txt
hv8880.nubes.rl.ak.uk MH-10000
hv8881.nubes.rl.ak.uk MH-10001
hv8882.nubes.rl.ak.uk MH-10002
hv8883.nubes.rl.ak.uk MH-10003

$ python generate_kayobe_commands.py etc/hypervisors.txt

ansible-playbook ansible/mellanox-enable-uefi-pxe.yml -i hv8880.nubes.rl.ak.uk,hv8881.nubes.rl.ak.uk,hv8882.nubes.rl.ak.uk,hv8883.nubes.rl.ak.uk, --extra-vars "pxe_target=hv8880.nubes.rl.ak.uk:hv8881.nubes.rl.ak.uk:hv8882.nubes.rl.ak.uk:hv8883.nubes.rl.ak.uk"

kayobe overcloud host configure -e selinux_do_reboot=true -kl hv8880.nubes.rl.ak.uk:hv8881.nubes.rl.ak.uk:hv8882.nubes.rl.ak.uk:hv8883.nubes.rl.ak.uk --limit hv8880.nubes.rl.ak.uk:hv8881.nubes.rl.ak.uk:hv8882.nubes.rl.ak.uk:hv8883.nubes.rl.ak.uk

kayobe overcloud service deploy -kl hv8880.nubes.rl.ak.uk:hv8881.nubes.rl.ak.uk:hv8882.nubes.rl.ak.uk:hv8883.nubes.rl.ak.uk --limit hv8880.nubes.rl.ak.uk:hv8881.nubes.rl.ak.uk:hv8882.nubes.rl.ak.uk:hv8883.nubes.rl.ak.uk
```

### wrapper scripts around the kayobe commands

In case that helps, there are wrapper bash scripts around the kayobe commands available in this Github repo. These wrappers perform the following steps:
- execute the kayobe command and redirect the output to a log file
- call a parser to extract the relevant parts from that log file:
    - every paragraph containing the string **fatal:**
    - every paragraph containing the string **PLAY RECAP**

The list of wrapper scripts is as follows:
- inventory_from_netbox.sh
- mellanox_playbook.sh
- kayobe_overcloud_deploy_controller.sh
- kayobe_overcloud_deploy_hypervisor.sh
- kayobe_overcloud_host_configure.sh

