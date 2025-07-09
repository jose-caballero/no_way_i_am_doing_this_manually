from dataclasses import dataclass, field
from typing import Optional
import yaml


@dataclass
class IcingaQueryCredentialsHandler:
    username: str
    password: str


@dataclass
class IcingaDowntimeCredentialsHandler:
    username: str
    password: str


@dataclass
class OpenstackCredentialsHandler:
    username: str
    password: str


@dataclass
class AlertmanagerCredentialsHandler:
    username: str
    password: str
    

@dataclass
class NetboxCredentialsHandler:
    api_token: str


@dataclass
class JiraCredentialsHandler:
    username: str
    api_token: str


@dataclass
class SSH:
    key_path: str
    username: str
    passphrase: str


@dataclass
class Aquilon:
    username: str
    password: str
    

@dataclass
class Kayobe:
    nopassfile: str
    username: str
    hostname: str
    prod_env_path: str


@dataclass
class CredentialsHandler:
    icinga_query: IcingaQueryCredentialsHandler = field(default=None)
    icinga_downtime: IcingaDowntimeCredentialsHandler = field(default=None)
    openstack: OpenstackCredentialsHandler  = field(default=None)
    alertmanager: AlertmanagerCredentialsHandler = field(default=None)
    netbox: NetboxCredentialsHandler = field(default=None)
    jira: JiraCredentialsHandler = field(default=None)
    ssh: SSH = field(default=None)
    aquilon: Aquilon = field(default=None)
    kayobe: Kayobe = field(default=None)

    def __init__(self, yaml_path: str):
        """
        Load credentials from the given YAML file
        """
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)

        self.icinga_query = IcingaQueryCredentialsHandler(**data['icinga_query'])
        self.icinga_downtime = IcingaDowntimeCredentialsHandler(**data['icinga_downtime'])
        self.openstack = OpenstackCredentialsHandler(**data['openstack'])
        self.alertmanager = AlertmanagerCredentialsHandler(**data['alertmanager'])
        self.netbox = NetboxCredentialsHandler(**data['netbox'])
        self.jira = JiraCredentialsHandler(**data['jira'])
        self.ssh = SSH(**data['ssh'])
        self.aquilon = Aquilon(**data['aquilon'])
        self.kayobe = Kayobe(**data['kayobe'])

