#BoardEvaluator.py
import tensorflow as tf
import sys
sys.path.append("../board_evaluation")
import model
import numpy as np

def _board_to_feature_cube(goBoard, color_to_move):
    enemy_color = goBoard.otherColor( color_to_move )
    feature_cube = np.zeros((19,19, 8))
    for row in range(goBoard.boardSize ):
        for col in range(goBoard.boardSize ):
            pos = (row,col)
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
    def predict_single_sample(self, feature_cube):
        y_pred = self.sess.run(self.y_conv, feed_dict={self.x:[feature_cube]})
        return np.reshape(y_pred, [19,19])

    #board - GoBoard object
    #returns [19,19] matrix of floats, each float in [0,1] indicating probability black owns the territory
    #at the end of the game
    def evaluate_board(self, goBoard, color_to_move):
        feature_cube = _board_to_feature_cube(goBoard, color_to_move)
        predicted_ownership = self.predict_single_sample(feature_cube)

        #the model was trained on predicting ownership of color to move
        #here we swap this back to predicting ownership of black
        if color_to_move == "w":
            for i in xrange(len(predicted_ownership)):
                for j in xrange(len(predicted_ownership)):
                    predicted_ownership[i][j] = 1 - predicted_ownership[i][j]
        return predicted_ownership
