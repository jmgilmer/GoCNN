#GoDriver.py
from __future__ import print_function
import numpy as np
import sys

#TODO: fix this relative path, it will cause an import error if gogui is not started from the visualization directory
sys.path.append("../thirdparty")

import GoCNN.thirdparty.GoBoard as GoBoard  #this is in the thirdparty directory
from  BoardEvaluator import BoardEvaluator

def _swap_color(color):
    if color == "b":
        return "w"
    elif color == "w":
        return "b"
    raise ValueError("color needs to be w or b")

'''
GoDriver contains a BoardEvaluator object which will load the tensorflow model and be able to make predictions
based on the current board. '''
class GoDriver:
    def __init__(self, tf_ckpt_path, BOARD_SIZE = 19):
        self.board_evaluator = BoardEvaluator(tf_ckpt_path)
        self.BOARD_SIZE = BOARD_SIZE
        self.color_to_move = "b"

    def reset_board(self):
        self.board = GoBoard.GoBoard(self.BOARD_SIZE)
        self.color_to_move = "b"

    def play(self, color, move):
        if move != 'pass':
            (row,col) = move
            self.board.applyMove( color, (row,col) )
        self.color_to_move = _swap_color(color)

    #returns [19,19] matrix of floats indicating the probability black will own the territory at the end
    #of the game
    def evaluate_current_board(self):
        if self.board is None:
            return np.zeros((19,19))
        return self.board_evaluator.evaluate_board(self.board, self.color_to_move)
