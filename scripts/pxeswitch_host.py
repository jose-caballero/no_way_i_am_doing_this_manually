import sys
sys.path.append("/var/quattor/templates/wup22514/lib/python/")

from myaq.host import Host


hv_name = sys.argv[1]
hv = Host(hv_name)

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

