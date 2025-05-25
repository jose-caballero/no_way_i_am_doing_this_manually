"""
JIRA Issue Creator Script
Creates JIRA issues from a list of words and updates the file with issue IDs.
"""

import os
import sys
import jira
import argparse

from credentialshandler import CredentialsHandler



def create_jira_issues_from_file(filename, creds):
   
    issue_type = "HyperVisor"
    project_key = "MH"


    # Connect to JIRA
    try:
        endpoint = "https://stfc.atlassian.net/"
        username = creds.jira.username
        token = creds.jira.api_token
        conn = jira.client.JIRA(server=endpoint, basic_auth=(username, token))
    except Exception as e:
        print(f"Error connecting to JIRA: {e}")
        return False
    
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
            # Create JIRA issue
            issue_dict = {
                'project': project_key,
                'summary': word,
                'description': f'Issue created for: {word}',
                'issuetype': {'name': issue_type},
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
    parser = argparse.ArgumentParser(
        description="Script to create the JIRA tickets"
    )
    parser.add_argument(
        '--hypervisors-file',
        default='hypervisors.txt',
        help='Path to the hypervisors file (default: hypervisors.txt)'
    )
    parser.add_argument(
        '--creds-file',
        default='creds.yaml',
        help='Path to the credentials file (default: creds.yaml)'
    )
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    credentials_handler = CredentialsHandler(args.creds_file)
    success = create_jira_issues_from_file(args.hypervisors_file, credentials_handler)

