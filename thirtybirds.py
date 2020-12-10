#!/usr/bin/python

"""
== major systems ==
network
    discovery
    pubsub
    reverse ssh
    security
reporting
    exception capture
    status and context capture
interfaces
    http interface
    bash interface
    logs
version control

synchronized time

== fix before proceeding ==

expand and clarify networking data format

create command-line interface system
    can be extended by app
    systems:
        network
        version control
        os_and_hardware

have clients send exceptions and status messages to controller

== future features ==

management interfaces
    web interface?
    interactive shell?
    log file that can be tailed

add authentication for raspberry pis
    authenticate on discover using certs?

send status and exceptions messages to controller

trim paths in status_receiver?

== future setup process ==

installers for Raspbian, Ubuntu, Windows, OSX

copyable disk images
    setup script:
        assign new hostname
        generate new ssh key

change password for pi
add thirtybirds user and run as that

"""
import copy
import logging
from logging.handlers import RotatingFileHandler
import os
import sys
import time

tb_path = os.path.dirname(os.path.realpath(__file__))
path_containing_tb_and_app = os.path.split(tb_path)[0]

from .network import host_info
from .network import thirtybirds_connection
#from .network import http_interface
from .version_control.software_management import Software_Management
from .reporting.exceptions import capture_exceptions
from .reporting.status.status_receiver import Status_Receiver 
from .reporting.hardware_management import Hardware_Management
from . import settings as tb_settings # this copy retains tb settings
from . import settings as settings # this copy gets collated with app settings

@capture_exceptions.Class
class Thirtybirds():
    """
    This class initializes, connects and organizes the Thirtybirds systems used in a typical application.  
    So a Thirtybirds app need only provide settings and the required parameters.
    This class also provides top-level access to the various systems it contains.
    """
    def __init__(
            self,
            app_settings,
            app_path,
            network_message_callback=None,
            network_status_change_callback=None,
            exception_callback=None
        ):
        self.app_settings = app_settings
        self.app_path = app_path
        self.network_message_callback = network_message_callback
        self.exception_callback = exception_callback
        self.network_status_change_callback = network_status_change_callback

    #def init(self):
        #########################
        ## E X C E P T I O N S ##
        #########################
        self.set_up_logging(self.app_path)
        capture_exceptions.init(self.exception_receiver)

        ##########################################
        ## B A S I C   N E T W O R K   I N F O  ##
        ##########################################
        self.hostinfo = host_info.Host_Info(
            online_status_change_receiver=self.network_status_change_receiver, 
            exception_receiver = self.exception_receiver)
        self.hostname = self.hostinfo.get_hostname()

        #############################################
        ## A P P L Y   L O C A L   S E T T I N G S ##
        #############################################
        self.collate_settings(settings, self.app_settings)
        self.status_type_names = [i for i in dir(settings.Reporting.Status_Types) if not (i[:2]=="__" and i[-2:]=="__")] 
        self.apply_flags()

        ###########################################################
        ## S T A R T   S T A T U S   M E S S A G E   S Y S T E M ##
        ###########################################################
        self.status_recvr = Status_Receiver(True, path_containing_tb_and_app, self.status_receiver)
        for status_type_name in self.status_type_names:
            capture_or_ignore = getattr(settings.Reporting.Status_Types, status_type_name)
            if capture_or_ignore:
                self.status_recvr.activate_capture_type(status_type_name)
            else:
                self.status_recvr.deactivate_capture_type(status_type_name)

        #####################################
        ## S T A R T   N E T W O R K I N G ##
        #####################################
        self.client_names = []
        for host,role in settings.Roles.hosts.items():
            if role == "controller":
                self.controller_hostname = host
            else:
                self.client_names.append(host)

        self.connection = thirtybirds_connection.Thirtybirds_Connection(
            self.hostinfo.get_local_ip(),
            hostname = self.hostname,
            controller_hostname = self.controller_hostname,
            client_names = self.client_names,
            discovery_multicast_group = settings.Network.discovery_multicast_group,
            discovery_multicast_port = settings.Network.discovery_multicast_port,
            discovery_response_port = settings.Network.discovery_response_port,
            pubsub_pub_port = settings.Network.pubsub_publish_port,
            network_message_receiver = self.network_message_receiver,
            exception_receiver = self.exception_receiver,
            status_receiver = self.status_recvr,
            network_status_change_receiver = self.network_status_change_callback,
            heartbeat_interval = settings.Network.heartbeat_interval,
            heartbeat_timeout_factor = settings.Network.heartbeat_timeout_factor,
            caller_interval = settings.Network.caller_interval
        )
        self.connection.subscribe_to_topic("__status__")
        self.connection.subscribe_to_topic("__error__")

        #############################################
        ## S O F T W A R E   A N D   U P D A T E S ##
        #############################################
        self.tb_software_management = Software_Management(
            tb_path,
            self.exception_receiver,
            self.status_recvr
        )
        self.app_software_management = Software_Management(
            self.app_path,
            self.exception_receiver,
            self.status_recvr
        )
        os_version = self.tb_software_management.get_os_version()

        ###############################################
        ## H A R D W A R E   M E A S U R E M E N T S ##
        ###############################################
        self.hardware_management = Hardware_Management(os_version["name"])
        # todo: add a thread that sends intermittent data

        #############################################
        ## S T A R T   H T T P   I N T E R F A C E ##
        #############################################
        #if self.hostname == self.controller_hostname:
        #    self.http_connector = http_interface.http_interface

        #####################################
        ## T O P   L E V E L   A C C E S S ##
        #####################################

        ## N E T W O R K I N G ##
        # queries
        self.get_hostname = self.hostinfo.get_hostname            
        self.get_local_ip = self.hostinfo.get_local_ip
        self.get_global_ip = self.hostinfo.get_global_ip
        self.get_online_status = self.hostinfo.get_online_status
        self.check_connections = self.connection.check_connections
        # commands
        self.publish = self.connection.send
        self.subscribe_to_topic = self.connection.subscribe_to_topic
        self.unsubscribe_from_topic = self.connection.unsubscribe_from_topic

        ## S O F T W A R E ##
        # queries
        self.get_os_version = self.tb_software_management.get_os_version
        self.tb_get_git_timestamp = self.tb_software_management.get_git_timestamp
        self.tb_get_scripts_version = self.tb_software_management.get_scripts_version
        self.app_get_git_timestamp = self.app_software_management.get_git_timestamp
        self.app_get_scripts_version = self.app_software_management.get_scripts_version
        # commands
        self.app_pull_from_github = self.app_software_management.pull_from_github
        self.app_run_update_scripts = self.app_software_management.run_update_scripts
        self.tb_pull_from_github = self.tb_software_management.pull_from_github
        self.tb_run_update_scripts = self.tb_software_management.run_update_scripts

        ## H A R D W A R E ##
        # queries
        self.get_core_temp = self.hardware_management.get_core_temp
        self.get_wifi_strength = self.hardware_management.get_wifi_strength
        self.get_core_voltage = self.hardware_management.get_core_voltage
        self.get_system_cpu = self.hardware_management.get_system_cpu
        self.get_system_uptime = self.hardware_management.get_system_uptime
        self.get_system_disk = self.hardware_management.get_system_disk
        self.get_memory_free = self.hardware_management.get_memory_free
        self.get_system_status = self.hardware_management.get_system_status
        # commands
        self.restart = self.hardware_management.restart
        self.shutdown = self.hardware_management.shutdown

        ## S T A T U S ##
        # commands
        self.activate_status_capture_type =  self.status_recvr.activate_capture_type
        self.deactivate_status_capture_type =  self.status_recvr.deactivate_capture_type

        ## E X C E P T I O N S ##
        # commands
        self.activate_exception_capture_type =  None # tbd
        self.deactivate_exception_capture_type =  None # tbd
        
        # move this to external?
        self.api_fields = { # for GUI
            "get_hostname":{
                "receives":{},
                "returns":{
                    "hostname":{
                        "type":"string",
                        "max":255,
                    }
                }
            },
            "get_local_ip":{
                "receives":{},
                "returns":{
                    "local ip address":{
                        "type":"string",
                        "max":255,
                    }
                }
            },
            "get_global_ip":{
                "receives":{},
                "returns":{
                    "global ip address":{
                        "type":"string",
                        "max":255,
                    }
                }
            },
            "get_online_status":{
                "receives":{},
                "returns":{
                    "online":{
                        "type":"bool",
                    }
                }
            },
            "check_connections":{
                "receives":{},
                "returns":{
                    "online":{
                        "type":"bool",
                    }
                }
            },
            "publish":{
                "receives":{
                    "topic":{
                        "max":63,
                        "required":True
                    },
                    "message":{
                        "max":63,
                        "required":True
                    },
                    "destination":{
                        "max":63,
                        "required":False
                    },
                },
                "returns":{}
            },
            "subscribe_to_topic":{
                "receives":{
                    "topic":{
                        "max":63,
                        "required":True
                    },
                },
                "returns":{}
            },
            "unsubscribe_from_topic":{
                "receives":{
                    "topic":{
                        "max":63,
                        "required":True
                    },
                },
                "returns":{}
            },
            "get_os_version":{
                "receives":{},
                "returns":{
                    "os version":{
                        "type":"string",
                        "max":255,
                    }
                }
            },
            "tb_get_git_timestamp":{
                "receives":{},
                "returns":{
                    "git timestamp":{
                        "type":"datetime",
                    }
                }
            },
            "tb_get_scripts_version":{
                "receives":{},
                "returns":{
                    "scripts version":{
                        "type":"integer",
                    }
                }
            },
            "app_get_git_timestamp":{
                "receives":{},
                "returns":{
                    "git timestamp":{
                        "type":"datetime",
                    }
                }
            },
            "app_get_scripts_version":{
                "receives":{},
                "returns":{
                    "scripts version":{
                        "type":"integer",
                    }
                }
            },
            "app_pull_from_github":{"receives":{},"returns":{}},
            "app_run_update_scripts":{"receives":{},"returns":{}},
            "tb_pull_from_github":{"receives":{},"returns":{}},
            "tb_run_update_scripts":{"receives":{},"returns":{}},
            "get_core_temp":{
                "receives":{},
                "returns":{
                    "core temp":{
                        "type":"integer",
                    }
                }
            },
            "get_wifi_strength":{
                "receives":{},
                "returns":{
                    "wifi strength":{
                        "type":"float",
                    }
                }
            },
            "get_core_voltage":{
                "receives":{},
                "returns":{
                    "core voltage":{
                        "type":"float",
                    }
                }
            },
            "get_system_cpu":{
                "receives":{},
                "returns":{
                    "system cpu":{
                        "type":"string",
                        "max":255,
                    }
                }
            },
            "get_system_uptime":{
                "receives":{},
                "returns":{
                    "system uptime":{
                        "type":"string",
                        "max":255,
                    }
                }
            },
            "get_system_disk":{
                "receives":{},
                "returns":{
                    "system disk":{
                        "type":"string",
                        "max":255,
                    }
                }
            },
            "get_memory_free":{
                "receives":{},
                "returns":{
                    "memory free":{
                        "type":"integer",
                    }
                }
            },
            "restart":{"receives":{},"returns":{}},
            "shutdown":{"receives":{},"returns":{}},
            "activate_status_capture_type":{
                "receives":{
                    "status type":{ # wrong name
                        "max":63,
                        "required":True
                    },
                },
                "returns":{}
            },
            "deactivate_status_capture_type":{
                "receives":{
                    "status type":{# wrong name
                        "max":63,
                        "required":True
                    },
                },
                "returns":{}
            },
            "activate_exception_capture_type":{
                "receives":{
                    "exception type":{# wrong name
                        "max":63,
                        "required":True
                    },
                },
                "returns":{}
            },
            "deactivate_exception_capture_type":{
                "receives":{
                    "exception type":{# wrong name
                        "max":63,
                        "required":True
                    },
                },
                "returns":{}
            },
        }


    def set_up_logging(self, app_path):
        log_directory = "{0}/logs/".format(app_path)
        try:
            os.listdir(log_directory)
        except FileNotFoundError:
            os.mkdir(log_directory)
            open("{0}/__init__.py".format(log_directory), 'a').close()

        status_logging_path = "{0}/status.log".format(log_directory)
        self.status_logger = logging.getLogger("status")
        self.status_logger.setLevel(logging.DEBUG)
        status_handler = RotatingFileHandler(status_logging_path, maxBytes=100000,backupCount=20)
        self.status_logger.addHandler(status_handler)
        
        error_logging_path = "{0}/error.log".format(log_directory)
        self.error_logger = logging.getLogger("error")
        self.error_logger.setLevel(logging.DEBUG)
        error_handler = RotatingFileHandler(error_logging_path, maxBytes=100000,backupCount=20)
        self.error_logger.addHandler(error_handler)
        
    def apply_flags(self):
        try:
            sys.argv[sys.argv.index("-help")]
            print("thirtybirds command line options:")
            print("  -hostname $hostname")
            print("    run as specified $hostname")
            print("  -update_on_start [true|false]")
            print("    run all version updates specified in settings")
            for status_type_name in status_type_names:
                print("  -{0} [capture|ignore]".format(status_type_name))
                print("    capture or ignore status messages for {0}".format(status_type_name))
            sys.exit(0)
        except ValueError:
            pass

        try:
            self.hostname = sys.argv[sys.argv.index("-hostname")+1]
        except ValueError as e:
            pass
        except IndexError as e:
            print("usage: python ____.py -hostname $hostname")
            sys.exit(0)

        try:
            update_on_start = sys.argv[sys.argv.index("-update_on_start")+1]
            settings.Version_Control.update_on_start = True if update_on_start == "true" else False
        except ValueError as e:
            pass
        except IndexError as e:
            print("usage: python ____.py -update_on_start [true|false]")
            sys.exit(0)

        for status_type_name in self.status_type_names:
            try:
                capture_or_ignore = sys.argv[sys.argv.index("-{0}".format(status_type_name))+1]
                setattr(settings.Reporting.Status_Types, self.status_type_name, True if capture_or_ignore == "true" else False)
            except ValueError as e:
                pass
            except IndexError as e:
                print("usage: python ____.py -{0} [capture|ignore]".format(status_type_name))
                sys.exit(0)

    def status_receiver(self, status_details):
        
        status_details_str = "{},{},{},{}{},{}.{},{},{}".format(
            time.strftime("%Y-%m-%d %H:%M:%S", status_details["time_local"]), 
            status_details["time_epoch"],
            status_details["hostname"],
            status_details["path"],
            status_details["script_name"], 
            status_details["class_name"],
            status_details["method_name"],
            status_details["message"],
            status_details["args"]
        )
        self.status_logger.error(status_details_str)
        if self.hostname != self.controller_hostname:
            try:
                #print(type(status_details), status_details)
                self.connection.send("__status__", status_details)
            except AttributeError:
                pass
        
    def exception_receiver(self, exception):
        # to do : add logging, if in config
        # if client, publish exceptions to controller
        # optional callback, though I don't know when it could be useful
        #print("exception_receiver",exception)
        exception_details_str = "{0},{1},{2},{3}{4},{5}.{6},{7},{8},{9},{10},{11}".format(
            time.strftime("%Y-%m-%d %H:%M:%S", exception["time_local"]), 
            exception["time_epoch"],
            exception["hostname"],
            exception["path"],
            exception["script_name"], 
            exception["class_name"],
            exception["method_name"],
            exception["args"],
            exception["kwargs"],
            exception["exception_type"],
            exception["exception_message"],
            exception["stacktrace"]
            )
        self.error_logger.error(exception_details_str)

        try:
            self.exception_callback(exception)
        except TypeError:
            pass

    def network_status_change_receiver(self, online_status):
        # todo: log loss of network
        # report change back to app.  it might be important to halt hardware
        #print("network_status_change_receiver",online_status)
        try:
            self.network_status_change_callback(online_status)
        except TypeError:
            pass

    def network_message_receiver(self, topic, message, origin, destination):
        #print("network_message_receiver",topic, message)
        if topic == b"__status__":
            if self.hostname == self.controller_hostname:
                # todo: this should not have to be here.  don't send time struct through JSON or switch to Python serializer
                message["time_local"] = time.struct_time(message["time_local"])
                #print("-------------",type(message["time_local"]), message["time_local"])
                self.status_receiver(message)
                #self.network_message_callback(topic, message)
            #log this    
        else:
            try:
                #print("--1",topic, message)
                self.network_message_callback(topic, message, origin, destination)
                #print("--2",topic, message)
            except TypeError:
                pass

    def collate_settings(self, base_settings_module, optional_settings_module):
        base_settings_classnames = [i for i in dir(base_settings_module) if not (i[:2]=="__" and i[-2:]=="__")] 
        optional_settings_classnames = [i for i in dir(optional_settings_module) if not (i[:2]=="__" and i[-2:]=="__")]
        for optional_settings_class in optional_settings_classnames:
            if optional_settings_class not in base_settings_classnames:
                setattr(base_settings_module, optional_settings_class, getattr(optional_settings_module, optional_settings_class))
            else:
                base_settings_class_ref = getattr(base_settings_module, optional_settings_class)
                optional_settings_class_ref = getattr(optional_settings_module, optional_settings_class)
                # todo: it would be more concise and idiomatic to do the following with multiple inheritance.  if possible.
                optional_settings_class_variable_names = [attr for attr in dir(optional_settings_class_ref) if not callable(getattr(optional_settings_class_ref, attr)) and not attr.startswith("__")]
                for optional_settings_class_variable_name in optional_settings_class_variable_names:
                    setattr(base_settings_class_ref, optional_settings_class_variable_name, getattr(optional_settings_class_ref, optional_settings_class_variable_name))
