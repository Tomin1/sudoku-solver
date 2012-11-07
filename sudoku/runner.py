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
from copy import deepcopy
from multiprocessing import Process, Value
from solver import Solver

class Runner(Process): # Runs Solver objects
    def __init__(self, queue, sudokus_ready, info_object):
        Process.__init__(self)
        self.queue = queue
        self.ready = sudokus_ready
        self.info = info_object
    
    def run(self,noloop=False):
        while self.info.solvers.value > 0:
            self.info.loops.value = self.info.loops.value + 1
            solver = self.queue.get()
            if not solver.run():
                self.info.dead_solvers.value = self.info.dead_solvers.value + 1
                self.info.solvers.value = self.info.solvers.value - 1
            else:
                if solver.done:
                    if solver.good: # if sudoku is completed
                        self.ready.put(solver)
                        self.info.solvers.value = self.info.solvers.value - 1
                        if (self.info.answers_wanted.value and 
                                self.info.answers_wanted.value <= 
                                self.ready.qsize()):
                            self.info.solvers.value = 0
                    else: # if sudoku is not completed
                        if solver.split_request: # actual splitting
                            self.info.splits.value = self.info.splits.value + 1
                            for number in solver.numbers:
                                tmp = Solver(deepcopy(solver.sudoku))
                                tmp.sudoku[solver.row][solver.col] = number
                                self.queue.put(tmp)
                                self.info.solvers.value = (
                                    self.info.solvers.value + 1)
                            self.info.solvers.value = (
                                self.info.solvers.value - 1)
                else: # if solver needs to work more
                    self.queue.put(solver)
                if noloop:
                    break

class Info(): # Info to be shared between Runners
    def __init__(self):
        self.max_solvers = Value('i',0) # max solvers
        self.splits = Value('i',0) # splits
        self.dead_solvers = Value('i',0) # solvers that ended deadlock
        self.solvers = Value('i',0) # solvers in queue
        self.loops = Value('i',0) # how many loops has run
        self.answers_wanted = Value('i',0) # how many answers are needed
    
    def getReadable(self,v,d=False): # Gives more readable representation of v
        if d:
            return str(v.value)
        
        a = v.value
        s = str(a)
        if a // 1000000:
            return s[:-6]+"M"+s[-6]
        if a // 1000:
            return s[:-3]+"k"+s[-3]
        return str(a)
