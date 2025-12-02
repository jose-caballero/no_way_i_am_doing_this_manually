"""JIRA Issue Creator Script

Creates JIRA issues from a list of hypervisors and updates the file with the
generated issue IDs.  If an issue already exists with the same summary the
existing issue key is used instead of creating a new ticket.
"""

import os
import sys
import jira
import argparse
import yaml



def create_jira_issues_from_file(filename, username, api_token):
    """
    Create Jira issues for each hypervisor listed in ``filename``.
    Parameters
    ----------
    filename : str
        Path to the file containing hypervisor names.
    username : str
        username allowed to create JIRA tickets
    api_token : str
        API token for that username
    Returns
    -------
    bool
        ``True`` if all issues were processed successfully, ``False`` otherwise.
    """
   
    issue_type = "HyperVisor"
    project_key = "MH"


    # Connect to JIRA
    try:
        endpoint = "https://stfc.atlassian.net/"
        conn = jira.client.JIRA(server=endpoint, basic_auth=(username, api_token))
    except Exception as e:
        print(f"Error connecting to JIRA: {e}")
        return False

    # get the accountId 
    my_accountId = conn.myself()['accountId']
    
    # Read the input file
    try:
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return False
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    if not lines:
        print("No words found in the file.")
        return False
    
    # Process each word and create JIRA issues
    updated_lines = []
    
    for i, word in enumerate(lines, 1):
        # Skip if line already has an issue ID (contains space)
        if ' ' in word:
            print(f"Skipping line {i}: '{word}' (already has issue ID)")
            updated_lines.append(word)
            continue
            
        try:
            # Check if an issue already exists with the same summary
            jql = f'project = {project_key} AND summary ~ "{word}"'
            existing = conn.search_issues(jql, maxResults=1)
            if existing:
                issue_key = existing[0].key
                print(f"Found existing issue {issue_key} for '{word}'")
                updated_lines.append(f"{word} {issue_key}")
                continue
        except Exception as e:
            print(f"Error searching existing issue for '{word}': {e}")

        try:
            # Create JIRA issue
            issue_dict = {
                'project': project_key,
                'summary': word,
                'description': f'Issue created for: {word}',
                'issuetype': {'name': issue_type},
                'assignee': {'accountId': my_accountId},
            }

            new_issue = conn.create_issue(fields=issue_dict)
            issue_key = new_issue.key

            print(f"Created issue {issue_key} for '{word}'")
            updated_lines.append(f"{word} {issue_key}")

        except Exception as e:
            print(f"Error creating issue for '{word}': {e}")
            # Keep the original word without issue ID if creation fails
            updated_lines.append(word)
    
    # Write updated content back to file
    try:
        with open(filename, 'w') as f:
            for line in updated_lines:
                f.write(line + '\n')
        print(f"\nFile '{filename}' updated successfully!")
        return True
    except Exception as e:
        print(f"Error writing to file: {e}")
        return False

    

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
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    with open(args.creds_file) as f: 
        config = yaml.safe_load(f)
    username = config["jira"]["username"] 
    api_token = config["jira"]["api_token"]
    success = create_jira_issues_from_file(args.hypervisors_file, username, api_token)

