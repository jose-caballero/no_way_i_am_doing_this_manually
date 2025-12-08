from dataclasses import dataclass, field
import yaml


@dataclass
class OpenstackCredentialsHandler:
    username: str
    password: str
    cloud: str


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
class General:
    initials: str


# --- Container that loads sections only if they exist ---

@dataclass
class CredentialsHandler:
    # Each attribute defaults to None so missing sections are allowed
    openstack: OpenstackCredentialsHandler = field(default=None)
    alertmanager: AlertmanagerCredentialsHandler = field(default=None)
    netbox: NetboxCredentialsHandler = field(default=None)
    jira: JiraCredentialsHandler = field(default=None)
    ssh: SSH = field(default=None)
    aquilon: Aquilon = field(default=None)
    kayobe: Kayobe = field(default=None)
    general: General = field(default=None)

    def __init__(self, yaml_path):
        """
        Load credentials from the given YAML file.
        Only creates section objects that are present in the YAML.
        """
        # Open the YAML file in read mode
        with open(yaml_path, 'r') as f:
            # Parse YAML; safe_load returns None on empty files, so coalesce to {}
            data = yaml.safe_load(f) or {}

        # Helper to safely build a section object or return None
        def load_section(key, cls):
            # Pick the subsection dict from the parsed data
            section = data.get(key)
            # If the section exists and is a mapping, build the dataclass with **kwargs
            if isinstance(section, dict):
                return cls(**section)
            # Otherwise, leave it unset (None)
            return None

        # Build each attribute only if its section is present
        self.openstack = load_section('openstack', OpenstackCredentialsHandler)
        self.alertmanager = load_section('alertmanager', AlertmanagerCredentialsHandler)
        self.netbox = load_section('netbox', NetboxCredentialsHandler)
        self.jira = load_section('jira', JiraCredentialsHandler)
        self.ssh = load_section('ssh', SSH)
        self.aquilon = load_section('aquilon', Aquilon)
        self.kayobe = load_section('kayobe', Kayobe)
        self.general = load_section('general', General)
