import subprocess


class Results:
    def __init__(self, cmd, stdout, stderr, rc):
        """
        container for the results of a command execution
        
        Parameters
        ----------
        cmd : str
            Command that was executed.
        stdout : str
            Standard output from the command.
        stderr : str
            Standard error from the command.
        rc : int
            Return code from the command.
        """
        self.cmd = cmd
        self.stdout = stdout.strip()
        self.stderr = stderr.strip()
        self.rc = rc

    @property
    def report_to_jira(self):
        """
        Format the execution results as a Jira code block.
        """
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
    """
    Run a shell command locally.
    Parameters
    ----------
    cmd : str
        Command line to execute.
    Returns
    -------
    Results
        Object containing the command output.
    """
    subproc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True)
    (out, err) = subproc.communicate()
    rc = subproc.returncode
    return Results(cmd, out, err, rc)

