# -*- coding: utf-8 -*-

import os
import shutil
import subprocess
import sys

try:
    import sensors #only for ubuntu
except ImportError:
    pass

root_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(root_path[0:root_path.find("/thirtybirds")])
from thirtybirds3.reporting.exceptions import capture_exceptions

#@capture_exceptions.Class
class Management(object):
    def __init__(
            self,
            tb_path,
            app_path
        ):
        self.app_path = app_path
        self.tb_path = tb_path
        self.os_name, self.os_version = self.get_os_version()
        
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
        return (name, version)

    def get_core_temp(self):
        if self.os_name == "ubuntu":
            sensors.init()
            max_temp = 0
            sensors.init()
            for chip in sensors.iter_detected_chips():
                for feature in chip:
                    if "Core" in feature.label:
                        core_temp = int(feature.get_value())
                        print(core_temp)
                        if core_temp > max_temp:
                            max_temp = core_temp
            sensors.cleanup()
            return max_temp

        if self.os_name == "raspbian":
            process = subprocess.run("/opt/vc/bin/vcgencmd measure_temp", shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
            return process.stdout[1][5:-2]

    def get_wifi_strength(self):
        process = subprocess.run('iwconfig', shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
        lines_from_bash_str = process.stdout
        lines_from_bash_l = lines_from_bash_str.split("\n")
        for line in lines_from_bash_l:
            try:
                start_postion = line.index("Link Quality")
                return int(line.split("Link Quality=")[1][:2])
            except ValueError:
                pass
        return -1


    def get_core_voltage(self):
        try:
            return float(commands.getstatusoutput("/opt/vc/bin/vcgencmd measure_volts core")[1])
            # ^ not formatted yet
        except Exception:
            return False


    def get_system_cpu(self):
        return [x / os.cpu_count() * 100 for x in os.getloadavg()][-1]

    def get_system_uptime(self):
        process = subprocess.run('uptime', shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
        lines_from_bash_str = process.stdout
        split_output = lines_from_bash_str.split(",")
        print(split_output)
        return False

    def get_system_disk(self):
        disk_usage = shutil.disk_usage("/")
        return disk_usage.free

    def get_memory_free(self):
        """
        returns free memory in bytes
        """
        process = subprocess.run('cat /proc/meminfo', shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
        lines_from_bash_str = process.stdout
        lines_from_bash_l = lines_from_bash_str.split("\n")
        for line in lines_from_bash_l:
            print(line)
            if line.startswith("MemFree:"):
                line_l = line.split()
                kb = float(line_l[1])
                mb = kb*1000.0
                return mb
        return -1


    def get_system_status(self):
        report = {
            "system_uptime":self.get_system_uptime(),
            "system_cpu":self.get_system_cpu(),
            "memory_free":self.get_memory_free(),
            "system_disk":self.get_system_disk(),
            "core_temp":self.get_core_temp(),
            "os_version":self.get_os_version(),
            "wifi_strength":self.get_wifi_strength()
        }
        return report
