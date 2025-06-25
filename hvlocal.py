import subprocess


class Results:
    def __init__(self, cmd, stdout, stderr, rc):
        self.cmd = cmd
        self.stdout = stdout.strip()
        self.stderr = stderr.strip()
        self.rc = rc

    @property
    def report_to_jira(self):
        msg = "command:"
        msg += "\n"
        msg += (
            "{code}"
            f'{self.cmd}'
            "{code}"
        )
        msg += "\n"
        msg += "stdout:"
        msg += "\n"
        msg += (
            "{code}"
            f'{self.stdout}'
            "{code}"
        )
        msg += "\n"
        msg += "stderr:"
        msg += "\n"
        msg += (
            "{code}"
            f'{self.stderr}'
            "{code}"
        )
        msg += "\n"
        msg += "return code:"
        msg += "\n"
        msg += (
            "{code}"
            f'{self.rc}'
            "{code}"
        )
        return msg


def run(cmd):
    subproc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True)
    (out, err) = subproc.communicate()
    rc = subproc.returncode
    return Results(cmd, out, err, rc)

