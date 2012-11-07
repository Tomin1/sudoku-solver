#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 
#  Printing tools
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
import sys

def print_msg(message): # prints normal message
    sys.stdout.write(message)
    sys.stdout.write("\n")

def print_err(message): # prints error message
    sys.stderr.write(message)
    sys.stderr.write("\n")

status_max_len = 0
def print_status(message):
    global status_max_len
    sys.stdout.write("\r")
    dif = status_max_len-len(message)
    if (dif > 0):
        sys.stdout.write(message+" "*dif)
    else:
        sys.stdout.write(message)
        status_max_len=len(message)
