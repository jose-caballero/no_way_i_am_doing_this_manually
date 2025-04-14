import jira
from logger import SetLogger


class HVJiraMessage:
    def __init__(self):
        self.text = "Message from automation library:\n"

    def add(self, text):
        self.text += "\n"
        self.text += text

    def add_block(self, text):
        self.text += "\n"
        self.text += (
            "{code}"
            f'{text}'
            "{code}"
        )


class HVJira(SetLogger):
    def __init__(self, hypervisormanager):
        self._set_logger()
        self.creds_handler = hypervisormanager.creds_handler
        self.issue_key = hypervisormanager.requeset.issue_key
        self.endpoint = "https://stfc.atlassian.net/"
        self.username = self.creds_handler.jira.username
        self.token = self.creds_handler.jira.api_token
        self.conn = jira.client.JIRA(server=self.endpoint, basic_auth=(self.username, self.token))
        self.log.debug("HVJira object created successfully")

    def add_comment(self, text):
        if isinstance(text, str):
            message = HVJiraMessage()
            message.add(text)
            text = message.text
        else:
            text = text.text
        self.conn.add_comment(self.issue_key, text, is_internal=True)

    def move_to_in_progress(self):
        self._change_state("In Progress")

    def move_to_working_on_pre_bios(self):
        self._change_state("Working On Pre Bios")

    def move_to_blocked(self):
        self._change_state("Blocked")

    def _change_state(self, new_state):
        allowed_transitions = self.conn.transitions(self.issue_key)
        for transition in allowed_transitions:
            # If we find the transition whose "to" state matches, perform the transition and return
            if transition["to"]["name"] == new_state:
                self.conn.transition_issue(self.issue_key, transition["id"])
                self.log.debug(f'jira issue {self.issue_key} moved to state {new_state}')
                break


