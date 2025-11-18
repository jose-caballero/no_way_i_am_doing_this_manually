import sys
sys.path.append("/var/quattor/templates/wup22514/lib/python/")

from myaq.host import Host
from myaq.personality import Personality
from myaq.archetype import Archetype
from myaq.operatingsystem import OperatingSystem
from myaq.profile import Profile
from myaq.location import Domain
from myaq.disk import Disk


hv_name = sys.argv[1]
hv = Host(hv_name)

archetype = Archetype("cloud")
personality = Personality("kayobe-prod", archetype=archetype)
#os = OperatingSystem("rocky", "9x-x86_64")
#profile = Profile(personality=personality, archetype=archetype, os=os)
#domain = Domain("prod_cloud_hvs")

#print(f"manging hypervisor {hv.name} to the right domain")
#results = domain._manage_host(hv)
#print("cmd: ")
#print(results.cmd)
#print("stdout: ")
#print(results.out)
#print("stderr: ")
#print(results.err)
#print("rc: ")
#print(results.rc)
#if results.rc != 0:
#    sys.exit()

if "a100" in hv_name:
    disk = Disk("sda")
    disk.remove(hv.machine)
    print("cmd: ")
    print(results.cmd)
    print("stdout: ")
    print(results.out)
    print("stderr: ")
    print(results.err)
    print("rc: ")
    print(results.rc)
    if results.rc != 0:
        sys.exit()

#results = hv.make_profile(profile)
results = hv.make(personality=personality)
print("cmd: ")
print(results.cmd)
print("stdout: ")
print(results.out)
print("stderr: ")
print(results.err)
print("rc: ")
print(results.rc)
if results.rc != 0:
    sys.exit()

results = hv.pxeswitch_install()
print("cmd: ")
print(results.cmd)
print("stdout: ")
print(results.out)
print("stderr: ")
print(results.err)
print("rc: ")
print(results.rc)
if results.rc != 0:
    sys.exit()

