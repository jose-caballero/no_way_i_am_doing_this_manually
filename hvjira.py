import jira


class HVJira:
    def __init__(self, creds_handler):
        self.creds_handler = creds_handler
        self.endpoint = "https://stfc.atlassian.net/"
        self.username = self.creds_handler.jira.username
        self.token = self.creds_handler.jira.api_token
        self.conn = jira.client.JIRA(server=self.endpoint, basic_auth=(self.username, self.token))

    def add_comment(self, issue_key, message):
        self.conn.add_comment(issue_key, message, is_internal=True)

    def move_to_in_progress(self, issue_key):
        self._change_state(issue_key, "In Progress")

    def move_to_blocked(self, issue_key):
        self._change_state(issue_key, "Blocked")

    def _change_state(self, issue_key, new_state):
        allowed_transitions = self.conn.transitions(issue_key)
        for transition in allowed_transitions:
            # If we find the transition whose "to" state matches, perform the transition and return
            if transition["to"]["name"] == new_state:
                conn.transition_issue(issue_key, transition["id"])
                break


