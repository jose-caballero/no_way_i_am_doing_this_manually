import jira

def get_list_of_jira_tickets(filename)
    jira_tickets_l = []
    with open(filename, 'r') as file:
        for line in file:
            # 1. Clean up the line (remove leading/trailing whitespace and newline characters)
            cleaned_line = line.strip()
            # Skip empty lines
            if not cleaned_line:
                continue
            # Skip commented out lines
            if cleaned_line.startswith('#'):
                continue
            # 2. Split the line into columns based on whitespace
            columns = cleaned_line.split()
            jira_tickets_l.append(columns[1])
    return jira_tickets_l

def update_jira_tickets(filename, username, api_token, comment):
    issue_type = "HyperVisor"
    project_key = "MH"

    # Connect to JIRA
    try:
        endpoint = "https://stfc.atlassian.net/"
        conn = jira.client.JIRA(server=endpoint, basic_auth=(username, api_token))
    except Exception as e:
        print(f"Error connecting to JIRA: {e}")
        return False
    jira_tickets_l = get_list_of_jira_tickets(filename)
    for ticket_id in jira_tickets_l:
        conn.add_comment(ticket_id, comment, is_internal=True)




# ==============================================================================
#   main
# ==============================================================================

def parse_arguments():
    """
    Parse command line arguments for the script
    """
    parser = argparse.ArgumentParser(
        description="Script to create the JIRA tickets"
    )
    parser.add_argument(
        '--hypervisors-file',
        default='etc/hypervisors.txt',
        help='Path to the hypervisors file (default: etc/hypervisors.txt)'
    )
    parser.add_argument(
        '--creds-file',
        default='etc/creds.yaml',
        help='Path to the credentials file (default: etc/creds.yaml)'
    )
    parser.add_argument(
        '--comment',
        help='comment to pass to all JIRA tickets'
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    with open(args.creds_file) as f:
        config = yaml.safe_load(f)
    username = config["jira"]["username"]
    api_token = config["jira"]["api_token"]
    success = update_jira_tickets(args.hypervisors_file, username, api_token, args.comment)

