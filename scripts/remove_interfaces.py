import sys
sys.path.append("/var/quattor/templates/wup22514/lib/python/")

from myaq.host import Host



hv_name = sys.argv[1]
hv = Host(hv_name)

machine = hv.machine

print(f"Interfaces information for HV {hv.name}\n")
interfaces = hv.interfaces
for interface in interfaces:
    print(interface.name)
    print(interface.addr)
    print(interface.ip)
    print()

for interface in interfaces:
    if interface.name not in ["bmc0", "eth0"]:
        if interface.ip != "":
            print(f"deleting interface address {interface.ip} for interface {interface.name} for HV {hv.name}")
            results = machine.remove_interface_address(interface)
            print(f"command: {results.cmd}")
            print(f"stdout: {results.out}")
            print(f"stderr: {results.err}")
            print(f"return code: {results.rc}")
        print(f"deleting interface {interface.name} for HV {hv.name}")
        results = machine.remove_interface(interface)
        print(f"command: {results.cmd}")
        print(f"stdout: {results.out}")
        print(f"stderr: {results.err}")
        print(f"return code: {results.rc}")

hv = Host(hv_name)
print(f"Updated list of interfaces for  HV {hv.name}\n")
interfaces = hv.interfaces
for interface in interfaces:
    print(interface.name)
    print(interface.addr)
    print(interface.ip)
    print()

