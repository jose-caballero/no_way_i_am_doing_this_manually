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

