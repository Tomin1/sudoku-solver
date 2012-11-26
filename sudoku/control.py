#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 
#  Tools for controlling runner objects 
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

"""Controlling runner objects"""

from sudoku.runner import Runner

def get_status(runners):
    """Returns some info about runner objects"""
    info = {
        'answers':runners[0].ready.qsize(),
        'solvers':runners[0].queue.qsize(),
        'dead':0,
        'splits':0,
        'loops':0
    }
    for runner in runners:
        if runner.running.value:
            info['solvers'] += 1
        info['dead'] += runner.dead.value
        info['splits'] += runner.splits.value
        info['loops'] += runner.loops.value
    return info

def start(sudoku,number_of_runners,number_of_answers=None):
    """Begins solving sudokus, uses multithreading"""
    from multiprocessing import JoinableQueue, Process, Queue
    wip_solvers = JoinableQueue() # Queue for wip Solvers
    done_solvers = Queue() # Queue for sudokus that are done
    wip_solvers.put(sudoku)
    runners = []
    for cur in range(number_of_runners):
        runners.append(Runner(wip_solvers,done_solvers))
        runners[cur].daemon = True
        runners[cur].start()
    return runners


def loop_check(runners,answers_wanted=0):
    """Regular checks to stop runners when queue is empty"""
    if answers_wanted != 0 and runners[0].ready.qsize() >= answers_wanted:
        return runners[0].ready
    if runners[0].queue.empty():
        for runner in runners:
            if runner.running.value:
                return False
        return runner.ready
    return False
