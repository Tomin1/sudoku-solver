#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# This is supposed to solve Sudokus
# Made by Tomin (http://tomin.dy.fi/)
# ALL THE CODE BELONGS TO HIM!
# YOU ARE FORBIDDEN TO USE OR COPY THIS CODE (for now)!
# © Tomi Leppänen (aka Tomin), 2011, ALL RIGHTS RESERVED!
import sys
from copy import deepcopy

RETRIES_DEFAULT = 3

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

def parse_string(sudoku): # parses array from sudoku
    s = ""
    for row in sudoku:
        for cell in row:
            if s != "":
                s = s+","+str(cell)
            else:
                s = str(cell)
    return s

def print_msg(message): # prints normal message
    sys.stdout.write(message)
    sys.stdout.write("\n")

def print_err(message): # prints error message
    sys.stderr.write(message)
    sys.stderr.write("\n")

def print_status(message):
    sys.stdout.write("\r")
    sys.stdout.write(message)

class Solver: # the Solver object
    def __init__(self, sudoku):
        self.sudoku = sudoku
        self.done = False # if Solver should be stopped
        self.good = False # if sudoku is completed
        self.split_mode = False # if split mode is on or not :)
        self.split_numbers = 10
        self.split_request = False # if split is requested or not
        self.retries = RETRIES_DEFAULT
        
    def get_grid(self,row,col): # checks which grid is being procecced
        return [(row+3)/3,(col+3)/3]
        
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
        numbers = range(1,10)
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
        for r in range(x*3-3,x*3):
            for c in range(y*3-3,y*3):
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
                    elif len(numbers) >= 2 and self.split_mode != False:
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
            self.retries = self.retries-1
        else:
            self.retries = RETRIES_DEFAULT
        if self.retries <= 0: # checks for retries
            if self.isgood():
                self.split_mode = 1 # turns split mode on
            else: # give up if sudoku is faulty
                self.done = True
                self.good = False
                return True
        return False

def main(argv):
    # begin checks
    if len(argv) != 2:
        print_err("Usage: "+argv[0]+" sudoku as a string")
        return 2
    sudoku = parse_sudoku(sys.argv[1])
    if sudoku == -1:
        print_err("Invalid sudoku string!")
        return 2
    # begin solving
    wsolver = [] # array for wip Solvers
    wsolver.append(Solver(sudoku))
    if not wsolver[0].isgood(): # one more check
        print_err("Invalid sudoku!")
        return 2
    dsudoku = [] # array for sudokus that are done
    max_solvers = 0 # amount of max solvers
    splits = 0 # amount of splits
    dead_solvers = 0 # amount of Solvers that ended deadlock
    while(len(wsolver) > 0): # while there is something to do
        for cur in range(0,len(wsolver)):
            wsolver[cur].run()
            if wsolver[cur].done == True:
                if wsolver[cur].good == True: # if sudoku is completed
                    dsudoku.append(wsolver[cur].sudoku)
                    wsolver.remove(wsolver[cur])
                    break
                else: # if sudoku is not completed
                    if wsolver[cur].split_request == True: # actual splitting
                        splits = splits+1
                        for number in wsolver[cur].numbers:
                            tmp = Solver(deepcopy(wsolver[cur].sudoku))
                            tmp.sudoku[wsolver[cur].row][wsolver[cur].col] = \
                                number
                            wsolver.append(tmp)
                        wsolver.remove(wsolver[cur])
                        break
                    else: # if sudoku is faulty
                        wsolver.remove(wsolver[cur])
                        dead_solvers = dead_solvers+1
                        break
        # printing status
        if len(wsolver) > max_solvers: # keep eye on maximum solvers
            max_solvers = len(wsolver)
        print_status("Solvers: Running: "+str(len(wsolver))+ \
            " Maximum: "+str(max_solvers)+ \
            " Splits: "+str(splits)+ \
            " Dead: "+str(dead_solvers)+ \
            " Answers: "+str(len(dsudoku)))
    print_msg("") # prints newline
    # printing results
    if len(dsudoku) == 0:
        print_msg("Sudoku was not solved!")
        return 1
    else:
        print_msg("Answers: "+str(len(dsudoku)))
        for wsudoku in dsudoku:
            print_msg("One answer is:")
            for row in wsudoku:
                print_msg(str(row))
            print_msg(parse_string(wsudoku))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
