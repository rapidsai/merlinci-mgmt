# Removes the 'gpuCI-test-this' label from PR's across the organization

import requests
import json
import logging
import os
import sys


REPOS = ['Merlin']
modified_prs = []
unmodified_prs = []


gh_auth_user = os.environ['GITHUB_AUTH_USER']
gh_auth_token = os.environ['GITHUB_AUTH_TOKEN']


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

def strip_labels(pr, label_to_remove):
    labels = list(filter(lambda label: label["name"] != label_to_remove, pr['labels']))
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

        # get prs that have the gpuCI-test-this label
        prs = list(filter(lambda pr: 'gpuCI-test-this' in list(map(lambda label: label["name"], pr["labels"])), prs))
        
        # remove 'gpuCI-test-this' label from label list
        prs = list(map(lambda pr: strip_labels(pr, 'gpuCI-test-this'), prs))

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
            print("No PRs were found with the gpuCI-test-this label")
        else:
            print(f"Removed labels from the following PRs:")
            for url in modified_prs:
                print(url)


if __name__ == '__main__':
    main()
