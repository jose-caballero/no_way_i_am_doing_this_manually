import jira

class HVJira:
    def __init__(self, hypervisormanager):
        """
        class to interact with JIRA and update the corresponding
        JIRA ticket for a given Hypervisor

        Parameters
        ----------
        hypervisormanager : HyperVisorManager
            Manager that owns this Jira helper.  Credentials and the issue
            key are retrieved from this object.
        """
        self.creds_handler = hypervisormanager.creds_handler
        self.issue_key = hypervisormanager.jira_issue_key
        self.endpoint = "https://stfc.atlassian.net/"
        self.username = self.creds_handler.jira.username
        self.token = self.creds_handler.jira.api_token
        self.conn = jira.client.JIRA(server=self.endpoint, basic_auth=(self.username, self.token))
        self.buffer = "Message from automation library:\n"

    def add(self, text):
        """
        Append text to the internal Jira message buffer.
        Parameters
        ----------
        text : str
            Text to append to the buffer.
        """
        self.buffer += "\n"
        self.buffer += text

    def add_block(self, text):
        """
        Append a block of text formatted for Jira code blocks.
        Parameters
        ----------
        text : str
            Text to include in a Jira ``{code}`` block.
        """
        self.buffer += "\n"
        self.buffer += (
            "{code}"
            f'{text}'
            "{code}"
        )

    def send_buffer(self):
        """
        Send the current buffer contents to Jira and reset it
        """
        self.conn.add_comment(self.issue_key, self.buffer, is_internal=True)
        self.buffer = "Message from automation library:\n"

    # =========================================================================
    #       transitions
    # =========================================================================

    def move_to_working_on_pre_bios(self):
        self._change_state("Working On Pre Bios")

    def move_to_pre_bios_failed(self):
        self._change_state("Pre Bios Failed")

    def move_to_draining(self):
        self._change_state("Draining")

    def move_to_drained(self):
        self._change_state("Drained")

    def move_to_ready_for_reinstall(self):
        self._change_state("Ready For Reinstall")

    # NOTE: this transition may never be triggered by the automation
    def move_to_working_on_reinstall(self):
        self._change_state("Working On Reinstall")

    def move_to_working_on_post_reinstall(self):
        self._change_state("Working On Post Reinstall")

    def move_to_ready_for_adoption(self):
        self._change_state("Ready For Adoption")

    # NOTE: this transition may never be triggered by the automation
    def move_to_working_on_adoption(self):
        self._change_state("Working On Adoption")

    def move_to_ready_for_test(self):
        self._change_state("Ready For Test")

    #def move_to_adoption_failed(self):
    #    self._change_state("Adoption Failed")


    def _change_state(self, new_state):
        """
        Perform a Jira workflow transition.
        Parameters
        ----------
        new_state : str
            Name of the target state as defined in Jira.
        """
        allowed_transitions = self.conn.transitions(self.issue_key)
        for transition in allowed_transitions:
            # If we find the transition whose "to" state matches, perform the transition and return
            if transition["to"]["name"] == new_state:
                self.conn.transition_issue(self.issue_key, transition["id"])
                break


