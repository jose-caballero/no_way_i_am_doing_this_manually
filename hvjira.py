import jira


class HVJira:
    def __init__(self, creds_handler, issue_key):
        self.creds_handler = creds_handler
        self.issue_key = issue_key
        self.endpoint = "https://stfc.atlassian.net/"
        self.username = self.creds_handler.jira.username
        self.token = self.creds_handler.jira.api_token
        self.conn = jira.client.JIRA(server=self.endpoint, basic_auth=(self.username, self.token))

    def add_comment(self, message):
        final_msg = f"Message from automation library:\n{message}"
        self.conn.add_comment(self.issue_key, final_msg, is_internal=True)

    def add_error(self, message, error):
        msg = (
            f"{message}"
            "\n"
            "{code}"
            f"{error}"
            "{code}"
        )
        self.add_comment(self.issue_key, msg)

    def move_to_in_progress(self):
        self._change_state(self.issue_key, "In Progress")

    def move_to_blocked(self):
        self._change_state(self.issue_key, "Blocked")

    def _change_state(self, new_state):
        allowed_transitions = self.conn.transitions(self.issue_key)
        for transition in allowed_transitions:
            # If we find the transition whose "to" state matches, perform the transition and return
            if transition["to"]["name"] == new_state:
                self.conn.transition_issue(self.issue_key, transition["id"])
                break


