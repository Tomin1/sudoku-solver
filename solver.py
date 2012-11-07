#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# This is supposed to solve Sudokus
# Made by Tomin (http://tomin.dy.fi/)
# ALL THE CODE BELONGS TO HIM!
# YOU ARE FORBIDDEN TO USE, MODIFY OR COPY THIS CODE (for now)!
# © 2011-2012, Tomi Leppänen (aka Tomin), ALL RIGHTS RESERVED!
import sys
from copy import deepcopy
from multiprocessing import Process, Manager, Value, active_children, cpu_count
from time import sleep

version = "v5"

def parse_sudoku(sudoku): # parses sudoku from array
    a = sudoku.split(",")
    if len(a) != 81:
        return -1
    sudoku = []
    for i in range(1,10):
        if len(a[(i*9-9):(i*9)]) != 9:
            return -1
        b = []
        for j in a[(i*9-9):(i*9)]:
            if j != "":
                try:
                    b.append(int(j))
                except ValueError:
                    return -1
            else:
                b.append("")
        sudoku.append(b)
    return sudoku

def print_msg(message): # prints normal message
    sys.stdout.write(message)
    sys.stdout.write("\n")

def print_err(message): # prints error message
    sys.stderr.write(message)
    sys.stderr.write("\n")

def print_status(message):
    sys.stdout.write("\r")
    sys.stdout.write(message)

def print_help(command):
    print_err('''Usage: '''+command+
        ''' [-h] [--help] [-1] [-t][<threads>] <sudoku>
-h --help       displays this help
-1              limits answers to only one
-t              use multiprocessing, uses as many threads as computer has CPUs
-t<threads>     use multiprocessing, uses number of <threads> threads
-V              prints version and licensing information''')

class Runner(Process): # Runs Solver objects
    def __init__(self, queue, sudokus_ready, info_object):
        Process.__init__(self)
        self.queue = queue
        self.ready = sudokus_ready
        self.info = info_object
    def run(self,noloop=False):
        while self.info.solvers_get() > 0:
            self.info.new_loop()
            solver = self.queue.get()
            solver.run()
            if solver.done == True:
                if solver.good == True: # if sudoku is completed
                    self.ready.put(solver)
                    self.info.solvers_dec()
                    if self.info.answers_wanted_get() <= self.ready.qsize():
                        self.info.solvers_kill()
                else: # if sudoku is not completed
                    if solver.split_request == True: # actual splitting
                        self.info.splits_inc()
                        for number in solver.numbers:
                            tmp = Solver(deepcopy(solver.sudoku))
                            tmp.sudoku[solver.row][solver.col] = number
                            self.queue.put(tmp)
                            self.info.solvers_inc()
                        self.info.solvers_dec()
                    else: # if sudoku is faulty
                        self.info.dead_solvers_inc() 
                        self.info.solvers_dec()
            else: # if solver needs to work more
                self.queue.put(solver)
            if noloop:
                break

class Solver(): # the Solver object
    def __init__(self, sudoku):
        self.sudoku = sudoku
        self.done = False # if Solver should be stopped
        self.good = False # if sudoku is completed
        self.split_mode = False # if split mode is on or not :)
        self.split_numbers = 10
        self.split_request = False # if split is requested or not
    
    def __str__(self):
        s = None
        for row in self.sudoku:
            for col in row:
                if s == None:
                    s = str(col)
                else:
                    s = s+","+str(col)
        return s
    
    def get_grid(self,row,col): # checks which grid is being procecced
        return [int((row+3)/3),int((col+3)/3)]
    
    def isgood_final(self): # checks if sudoku is correct, only for completed
        for a in range(0,9):
            suma = 0
            sumb = 0
            for b in range(0,9):
                suma = suma+self.sudoku[a][b]
                sumb = sumb+self.sudoku[b][a]
            if suma != 45 or sumb != 45:
                return False
        for r in range(1,4):
            for c in range(1,4):
                sumc = 0
                for r_n in range(r*3-3,r*3):
                    for c_n in range(c*3-3,c*3):
                        sumc = sumc+self.sudoku[r_n][c_n]
                if sumc != 45:
                    return False
        return True
    
    def isgood(self): # checks if sudoku is correct, slower
        for a in range(0,9):
            numbersa = []
            numbersb = []
            for b in range(0,9):
                if self.sudoku[a][b] != "":
                    try:
                        numbersa.index(self.sudoku[a][b])
                        return False
                    except ValueError:
                        numbersa.append(self.sudoku[a][b])
                if self.sudoku[b][a] != "":
                    try:
                        numbersb.index(self.sudoku[b][a])
                        return False
                    except ValueError:
                        numbersb.append(self.sudoku[b][a])
        for r in range(1,4):
            for c in range(1,4):
                numbersc = []
                for r_n in range(r*3-3,r*3):
                    for c_n in range(c*3-3,c*3):
                        if self.sudoku[r_n][c_n] != "":
                            try:
                                numbersc.index(self.sudoku[r_n][c_n])
                                return False
                            except ValueError:
                                numbersc.append(self.sudoku[r_n][c_n])
        return True
    
    def isready(self): # checks if all fields are filled
        for row in self.sudoku:
            try:
                row.index("")
                return False
            except ValueError:
                pass
        return True
    
    def get_numbers(self,row,col): # returns usable numbers
        numbers = []
        numbers.append(self.sudoku[row][col])
        numbers = list(range(1,10))
        for i in range(0,9):
            try:
                numbers.remove(self.sudoku[row][i])
            except ValueError:
                pass
            try:
                numbers.remove(self.sudoku[i][col])
            except ValueError:
                pass
        x,y = self.get_grid(row,col)
        for r in range(int(x*3-3),int(x*3)):
            for c in range(int(y*3-3),int(y*3)):
                if self.sudoku[r][c] != "":
                    try:
                        numbers.remove(self.sudoku[r][c])
                    except ValueError:
                        pass
        return numbers
    
    def run(self): # actual solving
        changed = False
        if self.isready():
            if self.isgood_final(): # if job is done, return True
                self.done = True
                self.good = True
                return True
            else:
                self.done = True
                self.good = False
                return True
        for row in range(0,9):
            for col in range(0,9):
                if self.sudoku[row][col] == "":
                    numbers = self.get_numbers(row,col)
                    if len(numbers) == 1:
                        changed = True # changed!
                        self.sudoku[row][col] = numbers[0]
                    elif len(numbers) == 0: # got into deadlock
                        self.done = True
                        self.good = False
                        return True
                    elif self.split_mode != False and len(numbers) >= 2:
                        changed = True # changed!
                        if self.split_mode == 1 and \
                                len(numbers) < self.split_numbers:
                            self.split_numbers = len(numbers)
                        elif self.split_mode == 2 and \
                                len(numbers) == self.split_numbers:
                            # prepare for splitting
                            self.numbers = numbers
                            self.row = row
                            self.col = col
                            self.done = True
                            self.good = False
                            self.split_request = True
                            return False # if sudoku is wip return False
        if self.split_mode == 1:
            self.split_mode = 2
        if changed == False: # if nothing has been solved in this round
            if self.isgood():
                self.split_mode = 1 # turns split mode on
            else: # give up if sudoku is faulty
                self.done = True
                self.good = False
                return True
        return False

class Info(): # Info to be shared between Runners
    def __init__(self):
        self.max_solvers = Value('i',0) # max solvers
        self.splits = Value('i',0) # splits
        self.dead_solvers = Value('i',0) # solvers that ended deadlock
        self.solvers = Value('i',0) # solvers in queue
        self.loops = Value('i',0)
    
    def solvers_inc(self,inc = 1):
        self.solvers.value = self.solvers.value + inc
    
    def solvers_dec(self,dec = 1):
        self.solvers.value = self.solvers.value - dec
        
    def solvers_kill(self):
        self.solvers.value = 0
        
    def solvers_get(self):
        return self.solvers.value
    
    def dead_solvers_inc(self,inc = 1):
        self.dead_solvers.value = self.dead_solvers.value + inc
        
    def dead_solvers_get(self):
        return self.dead_solvers.value
    
    def splits_inc(self,inc = 1):
        self.splits.value = self.splits.value + inc
        
    def splits_get(self):
        return self.splits.value
        
    def update_max_solvers(self):
        self.max_solvers.value = self.solvers.value
        
    def max_solvers_get(self):
        return self.max_solvers.value
    
    def answers_wanted_set(self,value):
        self.answers_wanted = value
    
    def answers_wanted_get(self):
        return self.answers_wanted
    
    def new_loop(self):
        self.loops.value = self.loops.value + 1
        
    def loops_get(self):
        return self.loops.value
    
def main(argv):
    # prepare some things
    answers_wanted = 0 # 0 means unlimited answers, default 0
    sudoku = 1 # which argument is sudoku, default 1
    use_threads = False # are threads used, default False
    # check arguments
    if len(argv) > 4 or len(argv) < 2:
        print_help(argv[0])
        return 2
    for arg in argv[1:]:
        if arg == "-h" or arg == "--help":
            print_help(argv[0])
            return 2
        elif arg == "-1":
            answers_wanted = 1
            sudoku = sudoku + 1
        elif "-t" in arg[0:2]:
            try:
                use_threads = int(arg[2:])
            except ValueError:
                use_threads = True
            sudoku = sudoku + 1
        elif arg == "-V":
            print_msg('''Sudoku Solver, version '''+version+'''
Made by Tomi Leppänen aka Tomin, ALL RIGHTS RESERVED!
You have no right to copy, redistribute, modify or use this code''')
    sudoku = parse_sudoku(argv[sudoku])
    if sudoku == -1:
        print_err("Invalid sudoku string!")
        return 2
    # begin solving
    manager = Manager() # Manager
    info = Info() # Info object with some shared information
    info.answers_wanted_set(answers_wanted)
    wsolver = manager.Queue() # Queue for wip Solvers
    dsudoku = manager.Queue() # Queue for sudokus that are done
    sudoku = Solver(sudoku)
    if not sudoku.isgood(): # one more check
        print_err("Invalid sudoku!")
        return 2
    wsolver.put(sudoku)
    info.solvers_inc()
    if use_threads:
        runners = [] # array for runners that use solvers
        if use_threads == True:
            max = cpu_count()
        else:
            max = use_threads
        for cur in range(0,max):
            runners.append(Runner(wsolver,dsudoku,info))
            runners[cur].start()
    else:
        runner = Runner(wsolver,dsudoku,info)
    while info.solvers_get() > 0: # while there is something to do
        # printing status
        if not use_threads:
            runner.run(True)
        else:
            sleep(0.05)
        if info.solvers_get() > info.max_solvers_get():
            info.update_max_solvers()
        if use_threads:
            running = len(runners)
        else:
            running = info.solvers_get()
        print_status("Solvers: Running: "+str(running)+ \
            " Maximum: "+str(info.max_solvers_get())+ \
            " Splits: "+str(info.splits_get())+ \
            " Dead: "+str(info.dead_solvers_get())+ \
            " Answers: "+str(dsudoku.qsize())+ \
            " Loops: "+str(info.loops_get())+"    ")
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
    try:
        sys.exit(main(sys.argv))
    except KeyboardInterrupt:
        print_msg("")
        raise
        sys.exit(2)
