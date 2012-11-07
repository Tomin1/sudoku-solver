#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 
#  Solver object
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

"""Solver object"""

class Solver():
    """Solver object
    
    This object solves sudokus. It can be used with tools to create sudoku 
    solver application or combined with Runner object to make life easier. 
    See Runner object in sudoku.runner for more information about it.
    """
    def __init__(self, sudoku):
        """Constructor
        
        sudoku parameter is an list created by parse_sudoku in sudoko.tools.
        """
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
    
    def get_grid(self,row,col):
        """checks which grid is being procecced"""
        return [int((row+3)/3),int((col+3)/3)]
    
    def isgood_final(self):
        """Checks if sudoku is completed correctly
        
        Use only for completed sudokus
        """
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
    
    def isgood(self):
        """Checks if a partial (or complete) sudoku is correct
        
        This is slower than isgood_final
        """
        for a in range(0,9):
            numbersa = []
            numbersb = []
            for b in range(0,9):
                if self.sudoku[a][b] != "":
                    try:
                        numbersa.index(self.sudoku[a][b])
                    except ValueError:
                        numbersa.append(self.sudoku[a][b])
                    else:
                        return False
                if self.sudoku[b][a] != "":
                    try:
                        numbersb.index(self.sudoku[b][a])
                    except ValueError:
                        numbersb.append(self.sudoku[b][a])
                    else:
                        return False
        for r in range(1,4):
            for c in range(1,4):
                numbersc = []
                for r_n in range(r*3-3,r*3):
                    for c_n in range(c*3-3,c*3):
                        if self.sudoku[r_n][c_n] != "":
                            try:
                                numbersc.index(self.sudoku[r_n][c_n])
                            except ValueError:
                                numbersc.append(self.sudoku[r_n][c_n])
                            else:
                                return False
        return True
    
    def isready(self):
        """Checks if all cells are filled"""
        for row in self.sudoku:
            try:
                row.index("")
            except ValueError:
                pass
            else:
                return False
        return True
    
    def get_numbers(self,row,col):
        """Returns numbers that can be filled into a cell"""
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
    
    def run(self):
        """Solves the sudoku
        
        This solves some of the sudoku and should be called until the sudoku 
        is ready. The status can be monitored using Sudoku objects good, done 
        and split_request attributes. Also returns False if something is wrong 
        otherwise returns True.
        """
        changed = False
        if self.isready():
            if self.isgood_final():
                self.done = True
                self.good = True
                return True
            else:
                self.done = True
                self.good = False
                return False
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
                        return False
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
                            return True
        if self.split_mode == 1:
            self.split_mode = 2
        if changed == False: # if nothing has been solved in this round
            if self.isgood():
                self.split_mode = 1 # turns split mode on
            else: # give up if sudoku is faulty
                self.done = True
                self.good = False
                return False
        return True
