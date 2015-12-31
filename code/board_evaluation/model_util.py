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
