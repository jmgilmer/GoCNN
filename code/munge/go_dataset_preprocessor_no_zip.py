#!/usr/bin/python
#
# Copyright Hugh Perkins 2015 hughperkins at gmail
#
# This Source Code Form is subject to the terms of the Mozilla Public License, 
# v. 2.0. If a copy of the MPL was not distributed with this file, You can 
# obtain one at http://mozilla.org/MPL/2.0/.

# assumptions:
# - at least python 2.7
# - not python 3.x
# - internet is available
# - on linux (since we're using signals)

#See main at bottom of file. This file will recursively traverse a directory for all .sgf files and convert the moves
#in those games to a binary format which can be used downstream for a CNN.

from __future__ import absolute_import, division

import sys,os,time, os.path
import shutil
import GoBoard
import signal
from os import sys, path
mydir = path.dirname(path.abspath(__file__))
print( mydir )
sys.path.append(mydir + '/gomill' )
import gomill
import gomill.sgf
import index_processor

import random
import numpy as np
import finish_games
import bit_writer

BOARD_SIZE = 19
OWNERSHIP_TARGET = True

def addToDataFile( datafile, color, move, goBoard, black_ownership, white_ownership ):
    # color is the color of the next person to move
    # move is the move they decided to make
    # goBoard represents the state of the board before they moved
    # - we should flip the board and color so we are basically always black
    # - we should calculate liberties at each position
    # - we should get ko
    # - and we should write to the file :-)
    #
    # planes we should write:
    # 0: our stones with 1 liberty
    # 1: our stones with 2 liberty
    # 2: our stones with 3 or more liberties
    # 3: their stones with 1 liberty
    # 4: their stones with 2 liberty
    # 5: their stones with 3 or more liberty
    # 6: simple ko
    # 7: board... 
    (row,col) = move
    enemyColor = goBoard.otherColor( color )
    datafile.write('GO') # write something first, so we can sync/validate on reading
    datafile.write(chr(row)) # write the move
    datafile.write(chr(col))

    if OWNERSHIP_TARGET:
        if color == 'b':
            ownership = black_ownership
        elif color =='w':
            ownership = white_ownership
        flattened_targets = [ownership[i][j] for i in xrange(BOARD_SIZE) for j in xrange(BOARD_SIZE)]
        num_bytes = bit_writer.write_sequence(flattened_targets, datafile)

    for row in range( 0, goBoard.boardSize ):
        for col in range( 0, goBoard.boardSize ):
            thisbyte = 0
            pos = (row,col)
            if goBoard.board.get(pos) == color:
                if goBoard.goStrings[pos].liberties.size() == 1:
                    thisbyte = thisbyte | 1
                elif goBoard.goStrings[pos].liberties.size() == 2:
                    thisbyte = thisbyte | 2
                else:
                    thisbyte = thisbyte | 4
            if goBoard.board.get(pos) == enemyColor:
                if goBoard.goStrings[pos].liberties.size() == 1:
                    thisbyte = thisbyte | 8
                elif goBoard.goStrings[pos].liberties.size() == 2:
                    thisbyte = thisbyte | 16
                else:
                    thisbyte = thisbyte | 32
            if goBoard.isSimpleKo( color, pos ):
                thisbyte = thisbyte | 64
            thisbyte = thisbyte | 128
            datafile.write( chr(thisbyte) )

def walkthroughSgf( sgfContents , sgfFilepath, output_file_name):
    sgf = gomill.sgf.Sgf_game.from_string( sgfContents )
    # print sgf
    try:
        if sgf.get_size() != BOARD_SIZE:
            print ('boardsize not %d, ignoring' %BOARD_SIZE )
            return
        goBoard = GoBoard.GoBoard(BOARD_SIZE)
        if sgf.get_handicap() != None and sgf.get_handicap() != 0:
            print 'handicap not zero, ignoring (' + str( sgf.get_handicap() ) + ')'
            return
    except:
        print "Error getting handicap. Ignoring this file"
        return
    moveIdx = 0

    black_ownership, white_ownership = None, None
    if OWNERSHIP_TARGET:
        black_ownership, white_ownership = finish_games.finish_sgf_and_get_ownership(sgfFilepath, 
            BOARD_SIZE, difference_treshold = 6, year_lowerbound = 0)
        if black_ownership is None or white_ownership is None:
            print "Unable to get final ownership for %s" %sgfFilepath
            return

    output_file = open(output_file_name , 'wb')

    for it in sgf.main_sequence_iter():
        (color,move) = it.get_move()
        if color != None and move != None:
            (row,col) = move
            addToDataFile( output_file, color, move, goBoard, black_ownership, white_ownership )
            try:
                goBoard.applyMove( color, (row,col) )
            except:
                print "exception caught at move %d" %(moveIdx)
                print "Ignoring the rest of this file"
                output_file.close()
                return
            moveIdx = moveIdx + 1
    output_file.close()
def munge_sgf( sgfFilepath, sgfFilename, output_file_name):
    sgf_file = open( sgfFilepath, 'r' )
    contents = sgf_file.read()
    sgf_file.close()

    if contents.find( 'SZ[%d]' %BOARD_SIZE ) < 0:
        print( 'not %dx%d, skipping: %s' %(BOARD_SIZE, BOARD_SIZE, sgfFilepath))
    try:
        walkthroughSgf( contents , sgfFilepath, output_file_name)
    except:
        print( "Weird exception happened caught for file " + path.abspath( sgfFilepath ) )
        print sys.exc_info()[0]
        print "Terminating the munging..."
        raise 
    #print( sgfFilepath )

#recursively traverse the source_dir directory and process every .sgf file in that directory.
#We ignore all files that are not BOARD_SIZExBOARD_SIZE, and skip handicap games. The GoGod dataset I downloaded
#had a few corrupted sgf files, these will be skipped as well. We write to train and test .dat files,
#where 1/test_mod fraction of samples is written to test instead of train.
def munge_all_sgfs( source_dir_path, output_dir_path):
    file_count = 0
    for subdir, dirs, files in os.walk(source_dir_path):
        for file in files:
            filepath = subdir + os.sep + file
            if file_count % 1000 == 0:
                print file_count
            if filepath.endswith(".sgf"):
                output_file_path = output_dir_path + os.sep + file[:-4] + ".dat"
                if os.path.isfile(output_file_path):
                    print "File already exists: %s" %output_file_path
                    continue
                munge_sgf(filepath, file, output_file_path)
                file_count+=1
    print "There were %d files" %(file_count)


if __name__ == '__main__':
    source_dir_path = "/home/justin/Programming/GoAI/Completing_Go_Games/pro_games/"
    output_dir_path = "/home/justin/Programming/GoAI/MovePredictionCNN/data/input/ownership_samples_all"
    munge_all_sgfs(source_dir_path, output_dir_path)
    print "Done munging"
 
