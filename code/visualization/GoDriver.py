#GoDriver.py
from __future__ import print_function
import numpy as np
import sys

#TODO: fix this relative path, it will cause an import error if gogui is not started from the visualization directory
sys.path.append("../thirdparty")

import GoBoard #this is in the thirdparty directory
import gomill.sgf
from  BoardEvaluator import BoardEvaluator

def _swap_color(color):
    if color == "b":
        return "w"
    elif color == "w":
        return "b"
    raise ValueError("color needs to be w or b")

'''
GoDriver has a pointer to a gomill.Sgf_game object which contains the game tree defined by an sgf file.
The current position in the file in maintained by the Sgf_game.main_sequence_iter() iterator.
It also contains a BoardEvaluator object which will load the tensorflow model and be able to make predictions
based on the current board. '''
class GoDriver:
    def __init__(self, sgf_filepath, tf_ckpt_path, BOARD_SIZE = 19):
        self.board_evaluator = BoardEvaluator(tf_ckpt_path)
        self.BOARD_SIZE = BOARD_SIZE
        self.load_sgf_file(sgf_filepath)
        self.color_to_move = "b"

    def load_sgf_file(self, sgf_filepath):
        with open(sgf_filepath, 'r') as sgf_file:
            sgfContents = sgf_file.read()
        self.sgf = gomill.sgf.Sgf_game.from_string( sgfContents)
        print("%s loaded. Winner: %s"%(sgf_filepath, self.sgf.get_winner()), file=sys.stderr)
        self.board = GoBoard.GoBoard(self.BOARD_SIZE)
        self.sgf_iterator = self.sgf.main_sequence_iter()

    def reset_board(self):
        self.board = GoBoard.GoBoard(self.BOARD_SIZE)
        self.sgf_iterator = self.sgf.main_sequence_iter()

    def gen_move(self):
        try:
            it = self.sgf_iterator.next()
            color, move = it.get_move()
            if move is None: #sometimes the first move isn't defined
                it = self.sgf_iterator.next()
                color, move = it.get_move()

        except StopIteration: #at the end of the file
            return "pass"

        if move is None:
            return "pass"

        self.color_to_move = _swap_color(color)
        (row,col) = move
        self.board.applyMove( color, (row,col) )
        return row, col

    #returns [19,19] matrix of floats indicating the probability black will own the territory at the end
    #of the game
    def evaluate_current_board(self):
        if self.board is None:
            return np.zeros((19,19))
        return self.board_evaluator.evaluate_board(self.board, self.color_to_move)