# Copyright Hugh Perkins 2015 hughperkins at gmail
#
# This Source Code Form is subject to the terms of the Mozilla Public License, 
# v. 2.0. If a copy of the MPL was not distributed with this file, You can 
# obtain one at http://mozilla.org/MPL/2.0/.

# doubly-indexed collection of locations on a board
# - given a location, can determine if it exists in the 'bag' of lcoations, in O(1)
# - can iterate over the locations, in time O(1) per locations
# - can remove a location, in O(1)
class Bag2d(object):
    def __init__(self, boardSize):
        self.boardSize = boardSize
        self.pieces = []
        self.board = {}

    def insert( self, combo ):
        ( row, col ) = combo
        if self.board.has_key(combo):
            return
        self.pieces.append( combo )
        self.board[combo] = len( self.pieces ) - 1

    def erase( self, combo ):
        if not self.board.has_key(combo):
            return
        i1d = self.board[combo]
        if i1d == len(self.pieces) - 1:
            del self.pieces[i1d]
            del self.board[combo]
            return
        self.pieces[i1d] = self.pieces[len(self.pieces) - 1]
        del self.pieces[len(self.pieces) - 1]
        movedcombo = self.pieces[i1d]
        self.board[movedcombo] = i1d
        del self.board[combo]

    def exists( self, combo ):
        return self.board.has_key(combo)

    def size(self):
        return len(self.pieces)

    def __getitem__( self, i1d ):
        return self.pieces[i1d]

    def __str__(self):
        result = 'Bag2d\n'
        for row in range(self.boardSize - 1, -1, -1 ):
            thisline = ""
            for col in range(0, self.boardSize):
                if self.exists( (row, col) ):
                    thisline = thisline + "*"
                else:
                    thisline = thisline + "."
            result = result + thisline + "\n"
        return result

