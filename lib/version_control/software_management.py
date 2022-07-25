#!/usr/bin/python

"""
Intended use:
This script sniffs and returns various network data about the host
"""

import importlib
import os
import pickle
import subprocess
import sys
import time

root_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(root_path[0:root_path.find("/thirtybirds")])
from thirtybirds3.reporting.exceptions import capture_exceptions

START_TIME = time.time()

#@capture_exceptions.Class
class Software_Management():
    def __init__(
            self, 
            path,
            exception_receiver,
            status_receiver):

        capture_exceptions.init(exception_receiver)
        self.path = path
        self.exception_receiver = exception_receiver
        self.status_receiver = status_receiver
        self.status_receiver.collect("starting",self.status_receiver.types.INITIALIZATIONS)
        self.version_control_path = "{}/version_control".format(self.path)
        self.version_pickle_path = "{}/version_pickle".format(self.version_control_path)
        self.scripts_path = "{}/scripts.py".format(self.version_control_path) 
        self.default_script_version_number = 0.0       
        # if version_control is not present don't try to use it. 
        # It's optional for app and should be added only through the repo
        self.using_scripts = True if os.path.isdir(self.version_control_path) else False

        if self.using_scripts and not os.path.isfile(self.version_pickle_path):
            self.set_scripts_version(self.default_script_version_number)
        self.status_receiver.collect("started",self.status_receiver.types.INITIALIZATIONS)

    def get_os_uptime(self):
        process = subprocess.run('uptime -s', shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
        return process.stdout.strip()

    def get_script_runtime(self):
        return time.time() - START_TIME

    def get_os_version(self):
        name = ""
        version = ""
        lines_from_bash = []
        process = subprocess.run('cat /etc/os-release', shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
        lines_from_bash_str = process.stdout
        lines_from_bash_l = lines_from_bash_str.split("\n")
        for line_from_bash in lines_from_bash_l:
            if line_from_bash.startswith("ID="):
                name = line_from_bash[line_from_bash.index("=")+1:].strip("\"")
            if line_from_bash.startswith("VERSION_ID="):
                version = line_from_bash[line_from_bash.index("=")+1:].strip("\"")
        return {"name":name, "version":version}

    def pull_from_github(self):
        bash_command = "cd {} && git pull -q --all -p".format(self.path)
        process = subprocess.run(bash_command, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
        return True if process.returncode == 0 else False

    def get_git_timestamp(self):
        process = subprocess.run("cd {}; git log -1 --format=%cd".format(self.path), shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
        git_timestamp =  process.stdout
        return git_timestamp.strip()

    def get_scripts_version(self):
        if self.using_scripts:
            with open(self.version_pickle_path, "rb") as pickle_file:
                return pickle.load(pickle_file)
        return 0.0

    def set_scripts_version(self, version):
        with open(self.version_pickle_path, "wb") as pickle_file:
            pickle.dump(float(version),pickle_file)

    def get_system_status(self):
        return {
            "uptime":self.get_os_uptime(),
            "runtime":self.get_script_runtime(),
            "os_version":self.get_os_version(),
            "app_git_timestamp":,
            "tb_git_timestamp":,
        }

    def run_update_scripts(self):
        command_errors = []
        if self.using_scripts:
            sys.path.append(self.version_control_path)
            update_scripts = importlib.import_module("update_scripts")
            version_numbers = list(update_scripts.scripts.keys())
            version_numbers.sort(key=float)
            version_from_pickle = self.get_scripts_version()
            for version_number in version_numbers:
                if float(version_number) > version_from_pickle:
                    bash_commands = update_scripts.scripts[version_number]
                    for bash_command in bash_commands:
                        try:
                            process = subprocess.run(bash_command, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
                        except Exception:
                            command_errors.append(bash_command)
            self.set_scripts_version(version_number)
        return command_errors
        