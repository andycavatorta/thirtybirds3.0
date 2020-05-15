#!/usr/bin/python
# -*- coding: ascii -*-

"""
Intended use:
This script creates and manages the conneciton between thirtybirds clients and their controller
"""

from . import discovery
from . import Network_Defaults



def discovery_handler(message):
    print("discovery_handler",message)


def init(
    ip_address,
    hostname,
    controller_hostname,
    discovery_multicastGroup,
    discovery_multicastPort,
    discovery_responsePort,
    pubsub_pubPort,
    pubsub_pubPort2):

    #role = Network_Defaults.DISCOVERY_ROLE_RESPONDER if hostname == controller_hostname else Network_Defaults.DISCOVERY_ROLE_CALLER

    tb_discovery = discovery.Discovery(
        ip_address = ip_address,
        hostname = hostname,
        controller_hostname = controller_hostname,
        discovery_multicastGroup = discovery_multicastGroup,
        discovery_multicastPort = discovery_multicastPort,
        discovery_responsePort = discovery_responsePort,
        caller_period = 10,
        callback = discovery_handler)

