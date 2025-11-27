import sys
sys.path.append("/var/quattor/templates/wup22514/lib/python/")

from myaq.host import Host
from myaq.personality import Personality
from myaq.location import Domain
from myaq.profile import Profile
from myaq.operatingsystem import OperatingSystem


hv_name = sys.argv[1]
hv = Host(hv_name)

# 
# Manage the Hypervisor to the right Domain
#
#domain = Domain("prod_cloud_hvs")
domain = Domain("prod")
results = domain._manage_host(hv)
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


# 
# Recompile the Hypervisor with the right Personality and OS version
#
personality = Personality("kayobe-prod", archetype=None)
os = OperatingSystem("rocky", "9x-x86_64")
profile = Profile(personality=personality, archetype=None, os=os)
results = hv.make_profile(profile)
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
