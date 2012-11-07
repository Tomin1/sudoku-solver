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

"""Runner and Info objects"""

from copy import deepcopy
try:
    from multiprocessing import Process, Value, Lock
except ImportError:
    from multiprocessing.dummy import Process, Value, Lock
from solver import Solver

class Runner(Process):
    """Runner object
    
    Object that solves sudokus using Solver. Creates necessary queues and 
    monitors sudoku's status. Uses multiprocessing.
    """
    def __init__(self, queue, sudokus_ready, info_object):
        """Constructor
        
        Arguments:
        queue -- Queue for unfinished sudokus
        sudokus_ready -- Queue for finished sudokus
        info_object -- See Info object in this module
        """
        Process.__init__(self)
        self.queue = queue
        self.ready = sudokus_ready
        self.info = info_object
    
    def run(self,noloop=False):
        """ See Python's Processing class's run method """
        while self.info.solvers.get() > 0:
            self.info.loops.inc()
            try:
                solver = self.queue.get()
            except EOFError:
                return
            if not solver.run():
                self.info.dead_solvers.inc()
                self.info.solvers.dec()
            else:
                if solver.done:
                    if solver.good: # if sudoku is completed
                        self.ready.put(solver)
                        self.info.solvers.dec()
                        if (self.info.answers_wanted.get() and 
                                self.info.answers_wanted.get() <= 
                                self.ready.qsize()):
                            self.info.solvers.set(0)
                    else: # if sudoku is not completed
                        if solver.split_request: # actual splitting
                            self.info.splits.inc()
                            for number in solver.numbers:
                                tmp = Solver(deepcopy(solver.sudoku))
                                tmp.sudoku[solver.row][solver.col] = number
                                self.queue.put(tmp)
                                self.info.solvers.inc()
                            self.info.solvers.dec()
                else: # if solver needs to work more
                    self.queue.put(solver)
                if noloop:
                    break

class Info:
    """Info object
    
    Contains information to be shared between runners.
    """
    def __init__(self):
        self.max_solvers = SharedInt() # max solvers
        self.splits = SharedInt() # splits
        self.dead_solvers = SharedInt() # solvers that ended deadlock
        self.solvers = SharedInt() # solvers in queue
        self.loops = SharedInt() # how many loops has run
        self.answers_wanted = SharedInt() # how many answers are needed
    
    def getReadable(self,value,d=False):
        """Gives more readable representation of value
        
        If d is True the value is returned as is.
        """
        if d:
            return str(value.get())
        
        a = value.get()
        s = str(a)
        if a // 1000000:
            return s[:-6]+"M"+s[-6]
        if a // 1000:
            return s[:-3]+"k"+s[-3]
        return str(a)

class SharedInt:
    """Integer in shared memory"""
    def __init__(self,value=0):
        self.lock = Lock()
        self.value = Value('i',value)
    
    def inc(self,inc=1):
        """Increases value"""
        with self.lock:
            self.value.value = self.value.value + inc
    
    def dec(self,dec=1):
        """Decreases value"""
        with self.lock:
            self.value.value = self.value.value - dec
    
    def get(self):
        """Returns value"""
        with self.lock:
            return self.value.value
    
    def set(self,value):
        """Sets new value"""
        with self.lock:
            self.value.value = value
