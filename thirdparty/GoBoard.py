# Copyright Hugh Perkins 2015 hughperkins at gmail
#
# This Source Code Form is subject to the terms of the Mozilla Public License, 
# v. 2.0. If a copy of the MPL was not distributed with this file, You can 
# obtain one at http://mozilla.org/MPL/2.0/.

import GoString
import Bag2d
import numpy as np

# a go board, can apply moves to it, contains gostrings, including their pieces, liberties etc
# can check for simple ko, and handle captures

def _fill(board, i, j, fill_val):
    if i < 0 or j < 0 or i >= len(board) or j >= len(board):
        return
    if board[i][j] != -1:
        return
    board[i][j] = fill_val
    _fill(board, i-1, j, fill_val)
    _fill(board, i+1, j, fill_val)
    _fill(board, i, j-1, fill_val)
    _fill(board, i, j+1, fill_val)
    

class GoBoard(object):
    def __init__( self, boardSize ) :
        self.ko_lastMoveNumCaptured = 0
        self.ko_lastMove = -3
        self.boardSize = boardSize
        self.board = {}  # I suppose it can be 'w', 'b' or nothing?
        self.goStrings = {}  # map of pos to gostring

    def foldStrings( self, targetString, sourceString, joinPos ):
        if( targetString == sourceString ):
            return

        for piecePos in sourceString.pieces.pieces:
            self.goStrings[piecePos] = targetString
            targetString.insertPiece( piecePos )

        # add the liberties from the second string
        targetString.copyLibertiesFrom( sourceString )
        targetString.removeLiberty( joinPos )

    def addAdjacentLiberty( self, pointString, pos ):
        (row,col) = pos
        if row < 0 or col < 0 or row >= self.boardSize or col >= self.boardSize:
            return
        if not self.board.has_key(pos):
            pointString.addLiberty(pos)

    # dont attempt to merge yet
    def createPointString( self, color, pos ):
        pointString = GoString.GoString( self.boardSize, color )
        pointString.insertPiece( pos )
        self.goStrings[pos] = pointString
        self.board[pos] = color
        
        (row,col) = pos
        for adjpos in [ (row-1,col), (row+1,col),(row,col-1), (row,col+1)]:
            self.addAdjacentLiberty( adjpos, pointString )

        return pointString

    def otherColor( self, color ):
        if color == 'b':
            return 'w'
        if color == 'w':
            return 'b'

    def isSimpleKo( self, playColor, pos ):
        enemyColor = self.otherColor( playColor )
        (row, col ) = pos
        # if exactly one stone captured on last move, then need to check for ko...
        if( self.ko_lastMoveNumCaptured == 1 ):
            # is the last move adjacent to us, and do we capture it?
            ( lastMoveRow, lastMoveCol ) = self.ko_lastMove
            manhattanDistanceLastMove = abs( lastMoveRow - row ) + abs( lastMoveCol - col )
            if( manhattanDistanceLastMove == 1 ):
                lastGoString = self.goStrings.get((lastMoveRow,lastMoveCol))
                if( lastGoString != None and lastGoString.numLiberties() == 1 ):
                    # apparently we do ....
                    # how many stones would we capture?  means, do we capture any others, that are 
                    # not the same string?
                    # first, check if this string has only one stone...
                    if( lastGoString.numPieces() == 1 ):
                        # apparently it does....
                        # any other adjacent enemy with no liberties?
                        totalNoLibertyAdjacentEnemy = 0
                        for adjpos in [ (row-1,col), (row+1,col),(row,col-1), (row,col+1)]:
                            if( self.board.get(adjpos) == enemyColor and
                                self.goStrings[adjpos].numLiberties() == 1 ):
                                totalNoLibertyAdjacentEnemy = totalNoLibertyAdjacentEnemy + 1
                        if( totalNoLibertyAdjacentEnemy == 1 ):
                            # it's a ko...
                            return True
        return False

    def checkEnemyLiberty( self, playColor, enemyPos, ourPos ):
        (enemyrow, enemycol) = enemyPos
        (ourrow, ourcol) = ourPos
#        print "checkEnemyLiberty enemy " + str(enemyPos) + " us " + str(ourPos)
        if( enemyrow < 0 or enemyrow >= self.boardSize or enemycol < 0 or enemycol >= self.boardSize ):
            return
        enemyColor = self.otherColor( playColor )
        if self.board.get(enemyPos) != enemyColor:
            # not enemy
#            print 'not enemy: ' + str(self.board.get(enemyPos)) + ' vs ' + str(enemyColor)
            return
        enemyString = self.goStrings[enemyPos]
        if( enemyString == None ):
            raise("checkenemyliberty 1 " )
#        print 'before removeliberty: ' + str( enemyString )
        enemyString.removeLiberty( ourPos )
#        print 'after removeliberty: ' + str( enemyString ) + ' numliberties:' + str(enemyString.numLiberties() )
        if( enemyString.numLiberties() == 0 ):
            # killed it!
            # remove all pieces of this string from the board
            # and remove the string
            # ko stuff
            for enemypos in enemyString.pieces.pieces:
                (stringrow,stringcol) = enemypos
                del self.board[enemypos]
                del self.goStrings[enemypos]
                self.ko_lastMoveNumCaptured = self.ko_lastMoveNumCaptured + 1
                for adjstring in [ (stringrow-1,stringcol),(stringrow+1,stringcol),(stringrow,stringcol-1),(stringrow,stringcol+1) ]:
                    self.addLibertyToAdjacentString( adjstring, enemypos, playColor )

    def applyMove( self, playColor, pos ):
        if self.board.has_key(pos):
           raise( "violated expectation: board[row][col] ==0, at " + str(pos) )

        self.ko_lastMoveNumCaptured = 0;

        (row,col) = pos
        # we need to remove any enemy that no longer has a liberty
        self.checkEnemyLiberty( playColor, ( row - 1, col), pos )
        self.checkEnemyLiberty( playColor, ( row + 1, col), pos )
        self.checkEnemyLiberty( playColor, ( row, col - 1), pos )
        self.checkEnemyLiberty( playColor, ( row, col + 1), pos )

        # then create a String for our new piece, and merge with any
        # adjacent strings
        playString = self.createPointString(playColor, pos)

        playString = self.foldStringIfOurs(playString, playColor, (row - 1, col), pos )
        playString = self.foldStringIfOurs(playString, playColor, (row + 1, col), pos )
        playString = self.foldStringIfOurs(playString, playColor, (row, col - 1), pos )
        playString = self.foldStringIfOurs(playString, playColor, (row, col + 1), pos )

        self.ko_lastMove = pos

    def addLibertyToAdjacentString( self, stringpos, libertypos, color ):
        if( self.board.get(stringpos) != color ):
            return
        goString = self.goStrings[stringpos]
        goString.insertLiberty( libertypos )

    def addAdjacentLiberty( self, pos, goString ):
        (row,col) = pos
        if row < 0 or col < 0 or row > self.boardSize - 1 or col > self.boardSize - 1:
            return
        if( not self.board.has_key(pos) ):
            goString.insertLiberty(pos)

    def foldStringIfOurs( self, string2, color, pos, joinpos ):
        (row,col) = pos
        if( row < 0 or row >= self.boardSize or col < 0 or col >= self.boardSize ):
            return string2
        if( self.board.get(pos) != color ):
            return string2
        string1 = self.goStrings[pos]
        self.foldStrings( string1, string2, joinpos )
        return string1

    def get_final_ownership(self, playColor):
        if playColor == 'b':
            otherColor = 'w'
        elif playColor == 'w':
            otherColor = 'b'
        else:
            raise ("playColor must be either b or w")
        board = np.full((self.boardSize,self.boardSize), -1)

        for i in range( 0, self.boardSize ):
            for j in range( 0, self.boardSize ):
                thispiece = self.board.get((i,j))
                if thispiece == playColor:
                    board[i][j] = 1
                if thispiece == otherColor:
                    board[i][j] = 0
        for i in range( 0, self.boardSize ):
            for j in range( 0, self.boardSize ):
                thispiece = self.board.get((i,j))
                if thispiece == playColor:
                    board[i][j] = 1
                    pass
                elif thispiece == otherColor:
                    board[i][j] = 0
                    pass
                else:
                    pass

        for i in range( 0, self.boardSize ):
            for j in range( 0, self.boardSize ):
                if board[i][j] != -1:
                    fill_val = board[i][j]
                    _fill(board, i-1, j, fill_val)
                    _fill(board, i+1, j, fill_val)
                    _fill(board, i, j-1, fill_val)
                    _fill(board, i, j+1, fill_val)
        return board

    def __str__(self):
        result = 'GoBoard\n'
        for i in range(self.boardSize - 1, -1, -1):
            line = ''
            for j in range(0,self.boardSize):
                thispiece = self.board.get((i,j))
                if thispiece == None:
                    line = line + '.'
                if thispiece == 'b':
                    line = line + '*'
                if thispiece == 'w':
                    line = line + 'O'
            result = result + line + '\n'
        return result

