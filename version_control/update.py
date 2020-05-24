#!/usr/bin/python

"""
Intended use:
This script sniffs and returns various network data about the host
"""


root_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(root_path[0:root_path.find("/thirtybirds")])
from thirtybirds3.reporting.exceptions import capture_exceptions

#@capture_exceptions.Class
class Update():
    def __init__(
        self, 
        update_on_start,
        github_repo_owner,
        github_repo_name,
        branch
        ):
        self.update_on_start = update_on_start
        self.github_repo_owner = github_repo_owner
        self.github_repo_name = github_repo_name
        self.branch = branch

        # if self.update_on_start

        # get local commit date
        # request HEAD commit date from github
        # if local date < HEAD date
        # git clone to sandbox?
        # if pull is not corrupted ( how to test?)
        # copy files from sandbox to root dir 
            # one at a time to preserve locals like settings, version.pickle, etc.
        # check 








