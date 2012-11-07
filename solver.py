#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# This is supposed to solve Sudokus
# Made by Tomin (http://tomin.dy.fi/)
# ALL THE CODE BELONGS TO HIM!
# YOU ARE FORBIDDEN TO USE OR COPY THIS CODE (for now)!
# © Tomi Leppänen (aka Tomin), 2011, ALL RIGHTS RESERVED!
import sys

def get_grid(row,cell):
    return [(row+3)/3,(cell+3)/3]

def isgood_final(sudoku): # checks if sudoku is correct
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

def isgood(sudoku): # checks if sudoku is correct
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

def isready(sudoku): # checks if sudoku has all fields filled
    for row in sudoku:
        try:
            row.index("")
            return False
        except ValueError:
            pass
    return True

def parse_sudoku(sudoku): # parses array to sudoku
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

def parse_string(sudoku): # parses sudoku to array
    s = ""
    for row in sudoku:
        for cell in row:
            if s != "":
                s = s+","+str(cell)
            else:
                s = str(cell)
    return s

def print_msg(message): # normal message
    sys.stdout.write(message)
    sys.stdout.write("\n")

def print_err(message): # error message
    sys.stderr.write(message)
    sys.stderr.write("\n")

def solve(sudoku): # solver function
    for row_n in range(0,9):
        for cell_n in range(0,9):
            if sudoku[row_n][cell_n] == "":
                numbers = range(1,10)
                for n in range(0,9):
                    if sudoku[row_n][n] != "":
                        try:
                            numbers.remove(sudoku[row_n][n])
                        except ValueError:
                            pass
                for n in range(0,9):
                    if sudoku[n][cell_n] != "":
                        try:
                            numbers.remove(sudoku[n][cell_n])
                        except ValueError:
                            pass
                r,c = get_grid(row_n,cell_n)
                for r_n in range(r*3-3,r*3):
                    for c_n in range(c*3-3,c*3):
                        if sudoku[r_n][c_n] != "":
                            try:
                                numbers.remove(sudoku[r_n][c_n])
                            except ValueError:
                                pass
                if len(numbers) == 1:
                    sudoku[row_n][cell_n] = numbers[0]
    return sudoku

def main(argv):
    if len(argv) != 2:
        print_err("Usage: "+argv[0]+" sudoku as a string")
        return 2
    sudoku = parse_sudoku(sys.argv[1])
    if sudoku == -1:
        print_err("Invalid sudoku string!")
        return 2
    old_sudoku = []
    retries = RETRIES_DEFAULT = 3
    while(not isready(sudoku)):
        sudoku = solve(sudoku)
        if old_sudoku == sudoku:
            if not isgood(sudoku):
                break
            retries -= 1
        else:
            retries = RETRIES_DEFAULT
        if retries <= 0:
            break
        old_sudoku = sudoku
    if not isready(sudoku):
        print_msg("Sudoku was not solved!")
        if not isgood(sudoku):
            print_msg("Sudoku is faulty!")
        retval = 1
    elif not isgood_final(sudoku):
        print_msg("Sudoku is not correct!")
        retval = 1
    else:
        print_msg("Sudoku is fine!")
        retval = 0
    for row in sudoku:
        print(row)
    print(parse_string(sudoku))
    return retval

if __name__ == "__main__":
    sys.exit(main(sys.argv))
