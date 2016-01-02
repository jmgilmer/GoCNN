import tensorflow as tf
import go_datafile_reader

#Visual the outputs of the model.
#Feature_cube: the x input of model, currently assumes first 6 planes are board position features
#y_pred: 19x19 matrix of thresholded prediction of final board ownership 
#y_val:  19x19 matrix of probabilities output by model
#y_true: 19x19 matrix of true board ownership
def print_info(feature_cube = None, y_pred = None, y_val = None, y_true = None):
    for i in xrange(19):
        current_row = ""
        if not feature_cube is None:
            for j in xrange(19):
                b_sum = feature_cube[i][j][0] + feature_cube[i][j][1] + feature_cube[i][j][2]
                w_sum = feature_cube[i][j][3] + feature_cube[i][j][4] + feature_cube[i][j][5]
                if b_sum > 0:
                    current_row += '1'
                elif w_sum > 0:
                    current_row += '0'
                else:
                    current_row += '*'
            current_row += "   "
        if not y_pred is None:
            for j in xrange(19):
                if y_pred[i][j] == 1:
                    current_row += '1'
                elif y_pred[i][j] == 0:
                    current_row += '0'
                else:
                    current_row += '*'
            current_row += "   "
        if not y_val is None:
            for j in xrange(19):
                val = round(10*y_val[i][j])
                if val >=10:
                    val = 9
                current_row+= "%d" %val
            current_row += "   "
        if not y_true is None:
            for j in xrange(19):
                if y_true[i][j] == 1:
                    current_row += '1'
                elif y_true[i][j] == 0:
                    current_row += '0'
                else:
                    current_row += '*'
            print current_row

def test_accuracy(features, targets, x, ownership, count_correct_op, BOARD_SIZE = 19):

    #I get a memory error when tf tries to feed the whole test set into my GPU, so we will do it in batches
    BATCH_SIZE = 100
    NUM_SAMPLES = len(features)
    batch_idx = 0

    num_correct = 0
    while batch_idx < NUM_SAMPLES:
        x_ = features[batch_idx:batch_idx+BATCH_SIZE]
        y_ = targets[batch_idx:batch_idx+BATCH_SIZE]
        num_correct += count_correct_op.eval(feed_dict = {x:x_, ownership:y_})
        batch_idx += BATCH_SIZE
    return float(num_correct)/ float(NUM_SAMPLES * BOARD_SIZE * BOARD_SIZE)