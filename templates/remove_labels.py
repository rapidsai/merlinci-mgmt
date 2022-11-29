# Removes the 'gpuCI-test-this' label from PR's across the organization
"""
export GITHUB_AUTH_USER=<username>
export GITHUB_AUTH_TOKEN=<token>

python ./remove_labels.py
"""

import requests
import json
import logging
import os
import sys


REPOS = ['Merlin', 'core', 'dataloader', 'models', 'Transformers4Rec', 'systems', 'NVTabular']
modified_prs = []
unmodified_prs = []


gh_auth_user = os.environ['GITHUB_AUTH_USER']
gh_auth_token = os.environ['GITHUB_AUTH_TOKEN']
label_to_remove = os.environ['LABEL_TO_REMOVE'] if 'LABEL_TO_REMOVE' in os.environ else 'gpuCI-test-this'


def get_request(url, success_code, auth=None):
    try:
        r = requests.get(url) if auth==None else requests.get(url, auth=auth)
        if r.status_code != success_code:
            raise Exception(r) 
        return r
    except Exception as error:
        logging.exception(error)
        sys.exit(1)

def patch_request(url, body, success_code):
    try:
        r = requests.patch(url, data=body, auth=(gh_auth_user, gh_auth_token))
        if r.status_code != success_code:
            raise Exception(r)
        return r
    except Exception as error:
        logging.exception(error)
        sys.exit(1)

def strip_labels(pr, unwanted_label):
    labels = list(filter(lambda label: label["name"] != unwanted_label, pr['labels']))
    pr['labels'] = labels
    return pr



def main():
    if gh_auth_token is None or gh_auth_user is None:
        raise Exception("Github credentials have not been set, exiting.")
        sys.exit(1)
    for repo in REPOS:
        r = get_request(f'https://api.github.com/repos/NVIDIA-Merlin/{repo}/pulls?state=open?page=50', 200, auth=(gh_auth_user, gh_auth_token))
        response = json.dumps(r.json())
        prs = json.loads(response)

        # get prs that have the 'label_to_remove' label
        prs = list(filter(lambda pr: label_to_remove in list(map(lambda label: label["name"], pr["labels"])), prs))
        
        # remove 'label_to_remove' label from label list
        prs = list(map(lambda pr: strip_labels(pr, label_to_remove), prs))

        # update the prs in GH
        for pr in prs:
            try:
                patch_request(f"https://api.github.com/repos/NVIDIA-Merlin/{repo}/issues/{pr['number']}", json.dumps({'labels': list(map(lambda label: label['name'], pr['labels']))}), 200)
                modified_prs.append(pr['html_url'])
            except:
                unmodified_prs.append(pr['html_url'])

    if (len(unmodified_prs) > 0):
        print(f"Operation failed for the following PRs:")
        for url in unmodified_prs:
            print(url)
    else:
        if len(modified_prs) < 1:
            print(f"No PRs were found with the {label_to_remove} label")
        else:
            print(f"Removed the '{label_to_remove}' label from the following PRs:")
            for url in modified_prs:
                print(url)


if __name__ == '__main__':
    main()
