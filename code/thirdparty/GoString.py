# Copyright Hugh Perkins 2015 hughperkins at gmail
#
# This Source Code Form is subject to the terms of the Mozilla Public License, 
# v. 2.0. If a copy of the MPL was not distributed with this file, You can 
# obtain one at http://mozilla.org/MPL/2.0/.

import Bag2d

# represents a string of contiguous pieces of one color on the board
# including we have a list of all its liberties, and therefore their count
class GoString(object):
    def __init__(self, boardSize, color ):
        self.boardSize = boardSize
        self.color = color
        self.liberties = Bag2d.Bag2d(boardSize)
        self.pieces = Bag2d.Bag2d(boardSize)

    def getPiece( self, index ):
        return self.pieces[index]

    def getLiberty( self, index ):
        return self.liberties[index]

    def insertPiece( self, combo ):
        self.pieces.insert( combo )

    def numPieces(self):
        return self.pieces.size()

    def removeLiberty( self, combo ):
        self.liberties.erase( combo )

    def numLiberties(self):
        return self.liberties.size()

    def insertLiberty( self, combo ):
         self.liberties.insert( combo )
    
    def copyLibertiesFrom( self, source ):
        for libertyPos in source.liberties.pieces:
            self.liberties.insert( libertyPos )

    def __str__(self):
        result = "GoString[ pieces=" + str(self.pieces) + " liberties=" + str(self.liberties) + " ]"
        return result

