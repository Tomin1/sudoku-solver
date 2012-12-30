#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 
#  Printing tools, version 0.3-python2.7
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

def print_msg(*messages,**kargs):
    """Prints normal messages, just like print
    
    I don't know if using print() is more efficient, but at least I got better 
    results using this custom function. 
    """
    separator = kargs.get('separator')
    for message in messages:
        stdout.write(str(message))
        if separator: 
            stdout.write(separator)
        else: 
            stdout.write(" ")
    stdout.write("\n")

def print_err(*messages,**kargs):
    """Prints error mesasges"""
    separator = kargs.get('separator')
    for message in messages:
        stderr.write(str(message))
        if separator: 
            stderr.write(separator)
        else: 
            stderr.write(" ")
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

def get_readable(value,dont_change=False):
    """Gives more readable representation of value
    
    If dont_change is True the value is returned as is.
    """
    if dont_change:
        return str(value)
    
    s = str(value)
    if value // 1000000:
        return s[:-6]+"M"+s[-6]
    if value // 1000:
        return s[:-3]+"k"+s[-3]
    return s
