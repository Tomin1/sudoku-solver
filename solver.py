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
-t              use multiprocessing, uses as many threads as computer has CPUs
-t<threads>     use multiprocessing, uses number of <threads> threads
-u              don't use suffixes in long numbers
-V              prints version and licensing information
"""

from util.printing import *
from sudoku.runner import *
from sudoku.solver import *
from sudoku.tools import *
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
        sudoku = parse_sudoku(sudoku)
    except SudokuError as e:
        print_err(e.value)
        return 2
    if not arguments["-t"]: # Some optimations when threads aren't used
        from multiprocessing.dummy import Process, Manager, Value
    else:
        from multiprocessing import Process, Manager, Value
    # begin solving
    manager = Manager() # Manager
    info = Info() # Info object with some shared information
    if arguments["-1"]: info.answers_wanted.value = 1
    else: info.answers_wanted.value = 0
    wsolver = manager.Queue() # Queue for wip Solvers
    dsudoku = manager.Queue() # Queue for sudokus that are done
    sudoku = Solver(sudoku)
    if not sudoku.isgood(): # one more check
        print_err("Invalid sudoku!")
        return 2
    wsolver.put(sudoku)
    info.solvers.value = info.solvers.value + 1
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
        for cur in range(0,max):
            runners.append(Runner(wsolver,dsudoku,info))
            runners[cur].start()
    else:
        runner = Runner(wsolver,dsudoku,info)
    while info.solvers.value > 0: # while there is something to do
        # printing status
        if arguments["-t"]:
            sleep(0.08)
        else:
            for i in range(0,50):
                runner.run(True)
        if info.solvers.value > info.max_solvers.value:
            info.max_solvers.value = info.solvers.value
        print_status(
            "Solvers: "+info.getReadable(info.solvers,arguments["-u"])+
            " Maximum: "+info.getReadable(info.max_solvers,arguments["-u"])+
            " Splits: "+info.getReadable(info.splits,arguments["-u"])+
            " Dead: "+info.getReadable(info.dead_solvers,arguments["-u"])+
            " Answers: "+str(dsudoku.qsize())+
            " Loops: "+info.getReadable(info.loops,arguments["-u"])+
            " Extra: "+str(wsolver.qsize()))
    print_msg("") # prints newline
    # printing results
    if dsudoku.qsize() == 0:
        print_msg("Sudoku was not solved!")
        return 1
    else:
        print_msg("Answers: "+str(dsudoku.qsize()))
        while not dsudoku.empty():
            wsudoku = dsudoku.get()
            print_msg("One answer is:")
            for row in wsudoku.sudoku:
                print_msg(str(row))
            print_msg(str(wsudoku))
    return 0

if __name__ == "__main__":
    import sys
    try:
        sys.exit(main(sys.argv))
    except KeyboardInterrupt:
        print_msg("")
        raise
