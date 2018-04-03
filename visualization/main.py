#!/usr/bin/python

'''
This file contains the main loop which communicates to gogui via the Go Text Protocol (gtp) via stdin.
When the predict ownership method is called we return the models board evaluation prediction on the
current state of the board.
'''

from __future__ import print_function
import sys
import re
import random
import numpy as np
import os
from .GoDriver import GoDriver

MODEL_PATH = "/home/tensorflow/src/GoCNN/data/working/board_eval_cnn_5layer.ckpt"


N = 19 #size of the board
letter_coords = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T']

#go from matrix index to board position string e.g. 0,2 -> A3
def coord_to_str(row, col):
    row = (19-1) - row
    return letter_coords[col] + str(row+1)

def str_to_coord(coord):
    row = int(coord[1:]) - 1
    col = letter_coords.index(coord[0].upper())
    return ( (19-1) - row, col)

#ownership_matrix - [N,N] matrix of floats output from the CNN model
#Formats a valid response string that can be fed into gogui as response to the 'predict_ownership' command
def influence_str(ownership_matrix):
    rtn_str = "INFLUENCE "
    for i in xrange(len(ownership_matrix)):
        for j in xrange(len(ownership_matrix)):
            rtn_str+= "%s %.1lf " %(coord_to_str(i,j), 2*(ownership_matrix[i][j] - .5)) #convert to [-1,1] scale
            #rtn_str+= " %.1lf\n" %(ownership_matrix[i][j])
    return rtn_str

def gtp_io():
    """ Main loop which communicates to gogui via GTP"""
    known_commands = ['boardsize', 'clear_board', 'komi', 'play',
                      'final_score', 'quit', 'name', 'version', 'known_command',
                      'list_commands', 'protocol_version', 'gogui-analyze_commands']
    analyze_commands = ["gfx/Final Ownership/predict_ownership"]
    driver = GoDriver(MODEL_PATH)

    print("starting main.py", file=sys.stderr)
    output_file = open("output.txt", "wb")
    output_file.write("intializing\n")
    while True:
        try:
            line = raw_input().strip()
            print(line,file=sys.stderr)
            output_file.write(line + "\n")
        except EOFError:
            output_file.write('Breaking!!\n')
            break
        if line == '':
            continue
        command = [s.lower() for s in line.split()]
        if re.match('\d+', command[0]):
            cmdid = command[0]
            command = command[1:]
        else:
            cmdid = ''
        ret = ''
        if command[0] == "boardsize":
            if int(command[1]) != N:
                print("Warning: Trying to set incompatible boardsize %s (!= %d)"%(command[1], N), file=sys.stderr)
        elif command[0] == "clear_board":
            driver.reset_board()
        elif command[0] == "komi":
            pass
        elif command[0] == "play":
            color = command[1][0]
            move = command[2]
            if move != 'pass':
                coord = str_to_coord(move)
                driver.play(color, coord)
            else:
                driver.play(color, move)                
            pass
            print("play", file=sys.stderr)
        elif command[0] == "final_score":
            print("final_score not implemented", file=sys.stderr)
        elif command[0] == "name":
            ret = 'board_evaluator'
        elif command[0] == "predict_ownership":
            ownership_prediction = driver.evaluate_current_board()
            ret = influence_str(ownership_prediction)
        elif command[0] == "version":
            ret = '1.0'
        elif command[0] == "list_commands":
            ret = '\n'.join(known_commands)
        elif command[0] == "gogui-analyze_commands":
            ret = '\n'.join(analyze_commands)

        elif command[0] == "known_command":
            ret = 'true' if command[1] in known_commands else 'false'
        elif command[0] == "protocol_version":
            ret = '2'
        elif command[0] == "quit":
            print('=%s \n\n' % (cmdid,), end='')
            break
        else:
            print('Warning: Ignoring unknown command - %s' % (line,), file=sys.stderr)
            ret = None

        if ret is not None:
            output_file.write("returning: '=%s %s'\n"%(cmdid, ret,))
            print('=%s %s\n\n' % (cmdid, ret,), end='')
        else:
            output_file.write("returning: '=?%s ???'\n"%(cmdid))
            print('?%s ???\n\n' % (cmdid,), end='')
        sys.stdout.flush()
    output_file.write('end of session\n')
    output_file.close()

if __name__ == '__main__':
    gtp_io()
