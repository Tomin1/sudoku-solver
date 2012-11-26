#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#  Sudoku Solver
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

"""Sudoku Solver

Copyright (C) 2011-2012, Tomi Leppänen
This program comes with ABSOLUTELY NO WARRANTY. This is free software, 
and you are welcome to redistribute it under certain conditions.
See LICENSE file for more information.

Usage: <the name of this file [-1] [-t[<threads>]] [-u] <sudoku>
or: <the name of this file> [-h] [-V]
-h              displays this help
-1              limits answers to only one
-t              use multiprocessing, uses as many threads as computer has 
                CPUs (default)
-t<threads>     use multiprocessing, uses number of <threads> threads
-u              don't use suffixes in long numbers
-V              prints version and licensing information
"""

from util.printing import *
from sudoku import *
# Does this cause any problems on systems without Python's multiprocessing?
from multiprocessing import cpu_count
from time import sleep

version = "v7"

def print_help(command):
    """Prints help"""
    print_msg(__doc__.replace("<the name of this file>",command))

def print_version(command):
    """Prints version information"""
    print_msg('''Sudoku Solver, version '''+version+'''
Copyright (C) 2011-2012, Tomi Leppänen
This program comes with ABSOLUTELY NO WARRANTY. This is free software, 
and you are welcome to redistribute it under certain conditions.
See LICENSE file for more information.''')

arguments = {
    "-h":False,
    "-1":False,
    "-t":"",
    "-u":False,
    "-V":False
}

def main(argv):
    """Main function
    
    This can be considered as a reference implementation of a sudoku solver.
    """
    sudoku = None
    # check arguments
    if len(argv) < 2:
        print_help(argv[0])
        return 2
    for arg in argv[1:]:
        for key,value in arguments.items():
            if arg.startswith(key):
                if arguments[key]:
                    print_err(key+" arguments given twice!")
                    return 2
                if arg == key:
                    arguments[key] = True
                    break
                arguments[key] = arg[len(key):]
                break
        else:
            sudoku = arg
    # help and version
    if arguments["-h"]:
        print_help(argv[0])
        return 0
    if arguments["-V"]:
        print_version(argv[0])
        return 0
    # try to parse sudoku
    try: 
        sudoku = tools.parse_sudoku(sudoku)
    except SudokuError as e:
        print_err(e.value)
        return 2
    # begin solving
    sudoku = solver.Solver(sudoku)
    if not sudoku.isgood(): # one more check
        print_err("Invalid sudoku!")
        return 2
    if arguments["-t"]:
        runners = [] # array for runners that use solvers
        if arguments["-t"] == True:
            max = cpu_count()
        else:
            try:
                max = int(arguments["-t"])
            except ValueError:
                print_err("Invalid value for thread count: "+arguments["-t"])
                return 2
        runners = control.start(sudoku,max)
    else:
        runners = control.start(sudoku,cpu_count())
    # printing status
    while True:
        info = control.get_status(runners)
        print_status(
            "Solvers:", get_readable(info['solvers'],arguments["-u"]),
            "Maximum:", get_readable(info['solvers']+info['dead'],
                                    arguments["-u"]),
            "Splits:", get_readable(info['splits'],arguments["-u"]),
            "Dead:", get_readable(info['dead'],arguments["-u"]),
            "Answers:", get_readable(info['answers'],arguments["-u"]),
            "Loops:", get_readable(info['loops'],arguments["-u"]))
        
        if arguments["-1"]:
            done = control.loop_check(runners,1)
        else:
            done = control.loop_check(runners)
        if done:
            break
        sleep(0.5)
    print_msg("") # prints newline
    # printing results
    if not info['answers']:
        print_msg("Sudoku was not solved!")
        return 1
    else:
        print_msg("Answers: "+str(info['answers']))
        while not done.empty():
            wsudoku = done.get()
            print_msg("One answer is:")
            for row in wsudoku.sudoku:
                print_msg(str(row))
            print_msg(str(wsudoku))
    return 0

if __name__ == "__main__":
    import sys
    try:
        sys.exit(main(sys.argv))
    except: # Add new line character after status line
        print_msg("")
        raise
