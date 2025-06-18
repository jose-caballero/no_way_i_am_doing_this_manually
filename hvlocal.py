import subprocess

def local_cmd(cmd):
    subproc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True)
    (out, err) = subproc.communicate()
    rc = subproc.returncode
    return out.strip(), err.strip(), rc
