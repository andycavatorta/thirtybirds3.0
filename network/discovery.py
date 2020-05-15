#!/usr/bin/python
# -*- coding: ascii -*-

"""
Intended use:
Multiple hosts on a LAN can use this script to create a self-assembling network.

One host is configured as the server and listens for IP broadcast messages
on a specific IP and port.  

Other hosts are configured as clients which send broadcast messages containing 
the client hostname and IP on a specific IP and port.  
When the server receives a broadcast message from a client, it sends a 
return message containg the server hostname and IP.
Both client and server report the interaction to a callback method that is passed 
into this module's init function.

This script may eventually support other methods such as connection brokers.
"""
