import sys
sys.path.append("/var/quattor/templates/wup22514/lib/python/")

from myaq.host import Host
from myaq.location import Sandbox


hv_name = sys.argv[1]
hv = Host(hv_name)

sandbox_name = "ieb35538/point_hvs_to_live_for_rl9_6"
sandbox = Sandbox(sandbox_name)

print(f'Managing HV {hv.name} to Sandbox {sandbox_name}')
results = sandbox._manage_host(hv)
print(f"command: {results.cmd}")
print(f"stdout: {results.out}")
print(f"stderr: {results.err}")
print(f"return code: {results.rc}")

