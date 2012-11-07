#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 
#  Tools for solving sudokus 
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

"""Tools for solving sudokus"""

def parse_sudoku(sudoku):
    """Parses sudoku from a string and returns a list"""
    if not sudoku:
        raise SudokuError('Sudoku undefined')
    a = sudoku.split(",")
    if len(a) != 81:
        raise SudokuError('Invalid sudoku string')
    sudoku = []
    for i in range(1,10):
        if len(a[(i*9-9):(i*9)]) != 9:
            raise SudokuError('Invalid sudoku string')
        b = []
        for j in a[(i*9-9):(i*9)]:
            if j != "":
                try:
                    b.append(int(j))
                except ValueError:
                    raise SudokuError('Invalid sudoku string')
            else:
                b.append("")
        sudoku.append(b)
    return sudoku

class SudokuError(Exception):
    """General exception for sudokus"""
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)
