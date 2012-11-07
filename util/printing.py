#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 
#  Printing tools, version 0.2
#  Copyright (C) 2011-2012, Tomi Leppänen (aka Tomin)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  

"""Printing tools

Tools to print messages, error messages and program status.
"""

from sys import stdout, stderr

def print_msg(*messages,separator=" "):
    """Prints normal messages, just like print
    
    I don't know if using print() is more efficient, but at least I got better 
    results using this custom function. 
    """
    for message in messages:
        stdout.write(str(message))
        stdout.write(separator)
    stdout.write("\n")

def print_err(*messages,separator=" "):
    """Prints error mesasges"""
    for message in messages:
        stderr.write(str(message))
        stderr.write(separator)
    stderr.write("\n")

status_max_len = 0
def print_status(*message):
    """Prints status message"""
    global status_max_len
    message = " ".join(message)
    stdout.write("\r")
    dif = status_max_len-len(message)
    if (dif > 0):
        stdout.write(message + " " * dif)
    else:
        stdout.write(message)
        status_max_len = len(message)
