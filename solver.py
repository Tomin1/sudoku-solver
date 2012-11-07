#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# This is supposed to solve Sudokus
# Made by Tomin (http://tomin.dy.fi/)
# ALL THE CODE BELONGS TO HIM!
# YOU ARE FORBIDDEN TO USE OR COPY THIS CODE (for now)!
# © Tomi Leppänen (aka Tomin), 2011, ALL RIGHTS RESERVED!
import sys
from copy import deepcopy

def get_grid(row,cell): # checks which grid is being procecced
    return [(row+3)/3,(cell+3)/3]

def isgood_final(sudoku): # checks if sudoku is correct, only for completed
    for a in range(0,9):
        suma = 0
        sumb = 0
        for b in range(0,9):
            suma += sudoku[a][b]
            sumb += sudoku[b][a]
        if suma != 45 or sumb != 45:
            return False
    for r in range(1,4):
        for c in range(1,4):
            sumc = 0
            for r_n in range(r*3-3,r*3):
                for c_n in range(c*3-3,c*3):
                    sumc += sudoku[r_n][c_n]
            if sumc != 45:
                return False
    return True

def isgood(sudoku): # checks if sudoku is correct, slower
    for a in range(0,9):
        numbersa = []
        numbersb = []
        for b in range(0,9):
            if sudoku[a][b] != "":
                try:
                    numbersa.index(sudoku[a][b])
                    return False
                except ValueError:
                    numbersa.append(sudoku[a][b])
            if sudoku[b][a] != "":
                try:
                    numbersb.index(sudoku[b][a])
                    return False
                except ValueError:
                    numbersb.append(sudoku[b][a])
    for r in range(1,4):
        for c in range(1,4):
            numbersc = []
            for r_n in range(r*3-3,r*3):
                for c_n in range(c*3-3,c*3):
                    if sudoku[r_n][c_n] != "":
                        try:
                            numbersc.index(sudoku[r_n][c_n])
                            return False
                        except ValueError:
                            numbersc.append(sudoku[r_n][c_n])
    return True

def isready(sudoku): # checks if all fields are filled
    for row in sudoku:
        try:
            row.index("")
            return False
        except ValueError:
            pass
    return True

def parse_sudoku(sudoku): # parses sudoku from array
    a = sudoku.split(",")
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

class Solver: # solver object
    def __init__(self, sudoku, row, cell):
        self.sudoku = sudoku
        self.row = row
        self.cell = cell
    def run(self):
        numbers = []
        numbers.append(self.sudoku[self.row][self.cell])
        if numbers[0] == "":
            numbers = range(1,10)
            for i in range(0,9):
                try:
                    numbers.remove(self.sudoku[self.row][i])
                except ValueError:
                    pass
                try:
                    numbers.remove(self.sudoku[i][self.cell])
                except ValueError:
                    pass
            x,y = get_grid(self.row,self.cell)
            for r in range(x*3-3,x*3):
                for c in range(y*3-3,y*3):
                    if self.sudoku[r][c] != "":
                        try:
                            numbers.remove(self.sudoku[r][c])
                        except ValueError:
                            pass
        return numbers

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
    wsudoku = [] # array for wip sudokus
    wsudoku.append(sudoku)
    dsudoku = [] # array for sudokus that are done
    retries = RETRIES_DEFAULT = 3
    split_mode = False # if split mode is on or not :)
    while(len(wsudoku) > 0):
        changed = False
        breaking = False
        for cur in range(0,len(wsudoku)):
            if isready(wsudoku[cur]): # if sudoku is solved it will be pushed
                if isgood_final(wsudoku[cur]): # to dsudoku array and
                    dsudoku.append(wsudoku[cur]) # removed from wsudoku array
                    wsudoku.remove(wsudoku[cur])
                    break
                else:
                    wsudoku.remove(wsudoku[cur])
                    break
            for row in range(0,9):
                for col in range(0,9):
                    if wsudoku[cur][row][col] == "":
                        numbers = Solver(wsudoku[cur],row,col).run()
                        if len(numbers) == 1:
                            changed = True
                            wsudoku[cur][row][col] = numbers[0]
                        elif len(numbers) >= 2:
                            if split_mode == True:
                                split_mode = False
                                for number in numbers:
                                    wsudoku.append(deepcopy(wsudoku[cur]))
                                    wsudoku[len(wsudoku)-1][row][col] = number
                                wsudoku.remove(wsudoku[cur])
                                breaking = True
                                break
                if breaking:
                    break
            if breaking:
                break
            if changed == False: # counts how many loops has gone without change
                retries =- 1
            else:
                retries = RETRIES_DEFAULT
            if retries <= 0: # checks for retries
                if isgood(wsudoku[cur]):
                    split_mode = True # turns split mode on
                else:
                    wsudoku.remove(wsudoku[cur])
                    break
    # printing results
    if len(dsudoku) == 0:
        print("Sudoku was not solved!")
        return 1
    else:
        print("Answers: "+str(len(dsudoku)))
        for wsudoku in dsudoku:
            print_msg("One answer is:")
            for row in wsudoku:
                print_msg(str(row))
            print_msg(parse_string(wsudoku))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
