# Scripts to Automate the Migration of HyperVisors to Rocky 9

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

```bash
git clone https://github.com/jose-caballero/no_way_i_am_doing_this_manually.git
cd no_way_i_am_doing_this_manually/
```

```bash
cp creds.yaml.template creds.yaml
vi creds.yaml
```

Edit the `creds.yaml` file and add your secrets.  
Ask around to get the credentials for services like Icinga, Alertmanager, etc.

```bash
cp hypervisors.txt.template hypervisors.txt
vi hypervisors.txt
```

Edit the `hypervisors.txt` file with the list of HVs you want to migrate.

### Copy scripts to remote hosts

* copy scripts/remove-host.sh to your account in Aquilon
* copy scripts/mellanox-playbook.sh to your kayobe environment server


## Execution 

To see the options, just run:

```bash
python ./run.py --help
```

Or use `python3` depending on your environment.

Example:

```bash
python ./run.py --step pre-reinstall
python ./run.py --step pre-reinstall --creds-file /path/to/my/creds.yaml
```

### `run.py` arguments

Below is a list of the available command line flags for `run.py`:

- `--hypervisors-file` - path to the file containing the list of hypervisors.
  Defaults to `hypervisors.txt`.
- `--creds-file` - path to the credentials file. Defaults to `creds.yaml`.
- `--step` - **required** step to run. Valid options are `setup`,
  `pre-drain`, `pre-reinstall`, `post-reinstall`, `adoption` and `noops`.
- `--parallel` - run the selected step in parallel mode. By default execution is
  serial and this flag must be provided to enable parallel runs.
