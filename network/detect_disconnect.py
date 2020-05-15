#!/usr/bin/python
# -*- coding: ascii -*-

"""
Intended use:
This script can receive a pub-sub socket and detects if an automatic 
periodic message does not arrive before a threshold period.
It can also generate such periodic messages for other hosts to receive.
The detection of disconnections can be useful for automatic reconnection.
"""
