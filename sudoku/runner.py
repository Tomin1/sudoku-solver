#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 
#  Runner and Info objects
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

"""Runner object"""

from copy import deepcopy
try:
    from multiprocessing import Process, RawValue
except ImportError:
    from multiprocessing.dummy import Process, RawValue
from sudoku.solver import Solver

class Runner(Process):
    """Runner object
    
    Object that solves sudokus using Solver. Creates necessary queues and 
    monitors sudoku's status. Uses multiprocessing.
    """
    def __init__(self, wip_queue, ready_queue):
        """Constructor
        
        Arguments:
        wip_queue -- Queue for unfinished sudokus
        ready_queue -- Queue for finished sudokus
        """
        Process.__init__(self)
        self.queue = wip_queue
        self.ready = ready_queue
        self.running = RawValue('b', False)
        self.dead = RawValue('i', 0)
        self.loops = RawValue('i', 0)
        self.splits = RawValue('i', 0)
    
    def run(self):
        """See Python's Processing class's run method, called by self.start()"""
        while True:
            solver = self.queue.get()
            if not solver: # Die if item is not a solver but None
                return
            self.running.value = True
            if solver.run():
                if solver.done:
                    self.queue.task_done()
                    if solver.good: # if sudoku is completed
                        self.ready.put(solver)
                    else: # if sudoku is not completed
                        if solver.split_request: # actual splitting
                            self.splits.value += 1
                            for number in solver.numbers:
                                tmp = Solver(deepcopy(solver.sudoku))
                                tmp.sudoku[solver.row][solver.col] = number
                                self.queue.put(tmp)
                else: # if solver needs to work more
                    self.queue.put(solver)
            else:
                self.queue.task_done()
                self.dead.value += 1
            self.running.value = False
            self.loops.value += 1
