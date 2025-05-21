import sys
sys.path.append("/var/quattor/templates/wup22514/lib/python/")


from myaq.host import Host
hv_name = sys.argv[1]

hv = Host(hv_name)
machine = hv.machine

interfaces = hv.interfaces
print(f"Interfaces information for HV {hv.name}")
for interface in interfaces:
    print(interface)

for interface in interfaces:
    if interface.name not in ["bmc0", "eth0"]:
        if interface.ip != "":
            print(f"deleting interface address {interface.ip} for interface {interface.name} for HV {hv.name}")
            machine.remove_interface_address(interface)
        print(f"deleting interface {interface.name} for HV {hv.name}")
        machine.remove_interface(interface)


