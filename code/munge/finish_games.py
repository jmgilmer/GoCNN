import subprocess
import re
import os
import numpy as np
import gomill
import gomill.sgf
import sys
sys.path.append("/home/justin/Programming/GoAI/kgsgo-dataset-preprocessor")
import GoBoard

TEMP_FILE = "/tmp/temp_gnu_output.sgfc"

def finish_sgf(sgf_filepath, dest_file = TEMP_FILE, BOARD_SIZE = 19, difference_treshold = 6, year_lowerbound = 0):
	dest_file = TEMP_FILE

	sgf_file = open(sgf_filepath, 'r')
	contents = sgf_file.read()
	sgf_file.close()

	move_count = contents.count(";")
	if move_count < 220:
		print "Too few moves: %s" %sgf_filepath
		return False

	if contents.find( 'SZ[%d]' %BOARD_SIZE ) < 0:
		print( 'not %dx%d, skipping: %s' %(BOARD_SIZE, BOARD_SIZE, sgf_filepath))
		return False
	match_str = r'RE\[([a-zA-Z0-9_\+\.]+)\]'
	m = re.search(match_str,contents)
	if m:
		result_str = m.group(1)
		pieces = result_str.split("+")
		try:
			winner = pieces[0]
			if pieces[1] == "R" or pieces[1] == "":
				return False
			score = float(pieces[1])
			if winner == "W":
				score*= -1
		except:
			print "Error parsing result, result_str = %s, file: %s" %(result_str, sgf_filepath)
			return False
	else:
		print "Couldn't find result, skipping: %s" %sgf_filepath
		return False

	match_str = r"DT\[([0-9]+)"
	m = re.search(match_str,contents)
	if m:
		year = int(m.group(1))
		if year < year_lowerbound:
			print "Game is too old: %s" %sgf_filepath
			return False

	print "Reading from: %s" %sgf_filepath
	print "Writing to: %s" %dest_file
	p = subprocess.Popen(["gnugo", "-l", sgf_filepath, "--outfile", dest_file, \
			"--score", "aftermath", "--capture-all-dead", "--chinese-rules"], stdout = subprocess.PIPE)
	output, err = p.communicate()
	m = re.search(r"([A-Za-z]+) wins by ([0-9\.]+) points", output)
	if m is None:
		return False
	winner = m.group(1)
	gnu_score = float(m.group(2))
	if winner == "White":
		gnu_score*=-1

	print score, gnu_score, winner
	if np.abs(score - gnu_score) > difference_treshold:
		print "GNU messed up finishing this game... removing %s" %dest_file
		os.remove(dest_file)
		return False
	return True

def get_final_ownership(gnu_sgf_outputfile, BOARD_SIZE = 19):
    sgffile = open(gnu_sgf_outputfile, 'r')
    sgfContents = sgffile.read()
    sgffile.close()

    sgf = gomill.sgf.Sgf_game.from_string( sgfContents )

    if sgf.get_size() != BOARD_SIZE:
        print ('boardsize not %d, ignoring' %BOARD_SIZE )
        return

    board = GoBoard.GoBoard(BOARD_SIZE)
    for move in sgf.root.get_setup_stones()[0]:
        board.applyMove("b", move)
    for move in sgf.root.get_setup_stones()[1]:
        board.applyMove("w", move)
    
    moveIdx = 0
    for it in sgf.main_sequence_iter():
        (color,move) = it.get_move()
        if color != None and move != None:
            (row,col) = move
            board.applyMove( color, (row,col) )
            moveIdx = moveIdx + 1
    
    black_ownership = board.get_final_ownership('b')
    white_ownership = np.zeros((BOARD_SIZE, BOARD_SIZE))
    for i in xrange(len(white_ownership)):
        for j in xrange(len(white_ownership)):
            if black_ownership[i][j] == 0:
                white_ownership[i][j] = 1
            else:
                white_ownership[i][j] = 0


    return black_ownership, white_ownership

def finish_sgf_and_get_ownership(sgf_filepath, BOARD_SIZE = 19, difference_treshold = 6, year_lowerbound = 0):
	if not(finish_sgf(sgf_filepath, TEMP_FILE, BOARD_SIZE, difference_treshold, year_lowerbound)):
		return None, None #failed to finish the game
	black_ownership, white_ownership = get_final_ownership(TEMP_FILE)
	return black_ownership, white_ownership

def traverse_directory( source_dir_path, dest_dir_path):
	file_count = 0
	for subdir, dirs, files in os.walk(source_dir_path):
		for file in files:
			filepath = subdir + os.sep + file
			if filepath.endswith(".sgf"):
				print file_count
				try:
					finish_sgf(filepath, file, dest_dir_path)
				except:
					print "Uncaught exception for %s" %filepath
				file_count+=1
	print "There were %d files" %(file_count)

###testing purposes
if __name__ == '__main__':
	source_dir = "/home/justin/Programming/GoAI/Completing_Go_Games/pro_games/1999/1/"
	dest_dir = "/home/justin/Programming/GoAI/Completing_Go_Games/finished_games/"
	filename = "YooChangHyuk-YangJaeHo24553.sgf"

	black_ownership, white_ownership = finish_sgf_and_get_ownership(source_dir + filename)

	for i in xrange(len(black_ownership)):
		row_str = ""
		for j in xrange(len(black_ownership)):
			row_str += str(int(black_ownership[i][j]))
		print row_str

