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

"""Runner and Pile object without multiprocessing depedency

These versions don't use multiprocessing but they are implemented only minimal 
changes compared to regular ones."""

from copy import deepcopy
from ctypes import c_byte, c_int
from queue import Queue
from sudoku.solver import Solver
try:
    from threading import Thread, Lock
except ImportError:
    from dummy_threading import Thread, Lock
from warnings import warn

class Pile(Queue):
    """Pile object
    
    Contains sudokus.
    """
    
    def __init__(self, maxsize=0):
        """Constructor
        
        Parameters:
        maxsize -- Maximium size of this Pile
        """
        Queue.__init__(self, maxsize)
        self._tasks = c_int(0)
        self._tasks_lock = Lock()
    
    def is_done(self):
        """Returns whether all tasks are done"""
        if self._tasks.value == 0:
            return True
    
    def put(self, obj, block=True, timeout=None):
        """Used when a task is put first time"""
        Queue.put(self, obj, block, timeout)
        self._tasks_lock.acquire()
        self._tasks.value += 1
        self._tasks_lock.release()
    
    def put_back(self, obj, block=True, timeout=None):
        """Used when a task is put back to be processed more"""
        Queue.put(self, obj, block, timeout)
    
    def task_done(self):
        """Called when task won't be put back
        
        Issues RuntimeWarning if all tasks are already done"""
        self._tasks_lock.acquire()
        if self._tasks.value <= 0:
            warn('All tasks are already done', RuntimeWarning)
        self._tasks.value -= 1
        self._tasks_lock.release()
    
    def tsize(self):
        """Returns how many tasks are left to do"""
        return self._tasks.value
        return False

class Runner(Thread):
    """Runner object
    
    Object that solves sudokus using Solver. Creates necessary queues and 
    monitors sudoku's status. Uses multiprocessing.
    
    Attributes:
    queue -- Pile (Queue) for unfinished sudokus
    ready -- Queue for finished sudokus
    
    Also available:
    running -- Is this Runner processing something
    dead -- Number of dead solvers
    loops -- Number of loops run
    splits -- Number of splits made by this Runner
    """
    
    queue = None
    ready = None
    
    def __init__(self, wip_queue, ready_queue):
        """Constructor
        
        Arguments:
        wip_queue -- Pile (Queue) for unfinished sudokus
        ready_queue -- Queue for finished sudokus
        """
        Thread.__init__(self)
        self.running = c_byte(False)
        self.dead = c_int(0)
        self.loops = c_int(0)
        self.splits = c_int(0)
        self.queue = wip_queue
        self.ready = ready_queue
    
    def run(self):
        """See multiprocessing.Process.run, called by self.start()"""
        while True:
            solver = self.queue.get()
            self.running.value = True
            if solver.run():
                if solver.done:
                    if solver.good: # if sudoku is completed
                        self.ready.put(solver)
                        self.queue.task_done()
                    else: # if sudoku is not completed
                        if solver.split_request: # actual splitting
                            self.splits.value += 1
                            for number in solver.numbers:
                                tmp = Solver(deepcopy(solver.sudoku))
                                tmp.sudoku[solver.row][solver.col] = number
                                self.queue.put(tmp)
                            self.queue.task_done()
                else: # if solver needs to work more
                    self.queue.put_back(solver)
            else:
                self.dead.value += 1
                self.queue.task_done()
            self.running.value = False
            self.loops.value += 1
        return
