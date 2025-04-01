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

## Execution

```bash
git clone https://github.com/jose-caballero/no_way_i_am_doing_this_manually.git
cd no_way_i_am_doing_this_manually/
```

```bash
vi creds.yaml
```

Edit the `creds.yaml` file and add your secrets.  
Ask around to get the credentials for services like Icinga, Alertmanager, etc.

```bash
vi hypervisors.txt
```

Edit the `hypervisors.txt` file with the list of HVs you want to migrate.

Then run:

```bash
python ./run.py --help
```

Or use `python3` depending on your environment.
