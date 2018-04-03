#BoardEvaluator.py
import tensorflow as tf
import sys
from ..board_evaluation import model
import numpy as np
import copy

def rotate_coord(coord, rot):
    (y, x) = coord
    size = 19
    if rot & 1:
        x = (size - 1) - x
    if rot & 2:
        y = (size - 1) - y
    if rot & 4:
        tmp = x
        x = y
        y = tmp
    return (y, x)


def _board_to_feature_cube(goBoard, color_to_move, rotation):
    enemy_color = goBoard.otherColor( color_to_move )
    feature_cube = np.zeros((19,19, 8))
    for row in range(goBoard.boardSize ):
        for col in range(goBoard.boardSize ):
            pos = rotate_coord((row, col), rotation)
            if goBoard.board.get(pos) == color_to_move:
                if goBoard.goStrings[pos].liberties.size() == 1:
                    feature_cube[row][col][0] = 1.0
                elif goBoard.goStrings[pos].liberties.size() == 2:
                    feature_cube[row][col][1] = 1.0
                else:
                    feature_cube[row][col][2] = 1.0
            if goBoard.board.get(pos) == enemy_color:
                if goBoard.goStrings[pos].liberties.size() == 1:
                    feature_cube[row][col][3] = 1.0
                elif goBoard.goStrings[pos].liberties.size() == 2:
                    feature_cube[row][col][4] = 1.0
                else:
                    feature_cube[row][col][5] = 1.0
            if goBoard.isSimpleKo( color_to_move, pos ): #FIX THIS!
                feature_cube[row][col][6] = 1.0
            feature_cube[row][col][7] = 1.0
    return feature_cube


class BoardEvaluator:
    def __init__(self, tf_ckpt_path):
        #init the tensorflow model
        self.x, _ = model.place_holders()
        self.y_conv = model.model(self.x)
        self.sess = tf.InteractiveSession()
        self.sess.run(tf.initialize_all_variables())
        saver = tf.train.Saver(tf.all_variables())
        saver.restore(self.sess, tf_ckpt_path)

    #feature_cube - [361,8] matrix of floats
    #returns - [19,19] matrix of probabilities
    def predict_single_sample(self, feature_cube, rotation):
        y_pred = self.sess.run(self.y_conv, feed_dict={self.x:[feature_cube]})
        res = np.reshape(y_pred, [19,19])
        out = copy.copy(res);
        for y in xrange(len(res)):
            for x in xrange(len(res)):
                (ry, rx) = rotate_coord((y, x), rotation)
                out[ry][rx] = res[y][x]
        return out

    #board - GoBoard object
    #rotation - rotation to use before sending to dcnn ([0-7], 0: no change)
    #returns [19,19] matrix of floats, each float in [0,1] indicating probability black owns the territory
    #at the end of the game
    def evaluate_board(self, goBoard, color_to_move, rotation):
        feature_cube = _board_to_feature_cube(goBoard, color_to_move, rotation)
        predicted_ownership = self.predict_single_sample(feature_cube, rotation)

        #the model was trained on predicting ownership of color to move
        #here we swap this back to predicting ownership of black
        if color_to_move == "w":
            for i in xrange(len(predicted_ownership)):
                for j in xrange(len(predicted_ownership)):
                    predicted_ownership[i][j] = 1 - predicted_ownership[i][j]
        return predicted_ownership
