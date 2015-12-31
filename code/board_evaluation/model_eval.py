import tensorflow as tf
import go_datafile_reader

def print_info(feature_cube, y_pred, y_true):
    for i in xrange(19):
        current_row = ""
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
        for j in xrange(19):
            if y_pred[i][j] == 1:
                current_row += '1'
            elif y_pred[i][j] == 0:
                current_row += '0'
            else:
                current_row += '*'
        current_row += "   "
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