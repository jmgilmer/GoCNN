import numpy as np
#Class GoDataset:
#opens a .dat file and keeps track of a location in that file. Extracts batches from the binary format and
#converts to numpy arrays which plug into tensorflow.

#The binary file has the following format (borrowed from Hugh Perkins kgs-go-dataset-preprocessor)
#Each sample contains 2 + 2 + 19*19 bytes. The first two bytes are 'GO' exist to help with
#data alignment. The next byte is an int giving the row of the move, row in [0,18]. Next is the column of the move.
#The next 19*19 = 361 bytes give the features at each board location. Each byte has the following bits:
#bit 0: location of mover stones with 1 liberty
#bit 1: location of mover stones with 2 liberties
#bit 3: location of mover stones with >= 3 liberties
#bit 4: location of opponent stones with 1 liberty
#bit 5: location of opponent stones with 2 liberties
#bit 6: location of opponent stones with >= 3 liberties
#bit 7: filler bit always = 1
#The last 2 bytes of the .dat file are 'ED' (for end)
class GoDataset:
	def __init__(self, data_filepath, board_size = 19):
		self.data_file = open(data_filepath, "rb")
		self.num_epochs = 0
		self.index_in_epoch = 0
		self.board_size = board_size
	def __del__(self):
		self.data_file.close()

	#read the next feature cube from the binary file. Note this will increment the position in the file.
	#This function assumes the bytes 'GO' and the target move byte have already been read
	def _get_feature_cube(self):
		feature_cube = np.zeros((self.board_size,self.board_size,7))
		for i in xrange(self.board_size):
			for j in xrange(self.board_size):
				feature_byte = ord(self.data_file.read(1))
				for k in xrange(7):
					feature_cube[i][j][k] = ((feature_byte >> k) & 1)
				assert(((feature_byte  >> 7) &1) == 1)
		return feature_cube

	#convert the int representing the move to a 1-hot array
	def _dense_to_onehot(self,y):
		num_labels = self.board_size **2
		assert(y >= 0 and y < num_labels)
		one_hot = np.zeros(num_labels)
		one_hot[y] = 1
		return one_hot

	#grab the next batch from the file and return the features, targets
	def next_batch(self, batch_size = 50):
		targets = []
		x_inputs = []
		for i in xrange(batch_size):
			go_byte = self.data_file.read(2) #this must be either GO or ED
			if go_byte != "GO":
				if go_byte == "ED": #we have reached the end of the file
					self.num_epochs+=1
					self.index_in_epoch=0
					self.data_file.seek(0) #goto the beginning of the file
					continue
				else: #datafile not synced
					raise AssertionError("Unexpected byte sequence in datafile.")
			row = ord(self.data_file.read(1))
			col = ord(self.data_file.read(1))
			targets.append(self._dense_to_onehot(row*self.board_size + col))
			x_inputs.append(self._get_feature_cube())
			self.index_in_epoch+=1
		return x_inputs, targets


### These were just used for testing purposes ###
def get_sum(x):
	total = 0
	for i in xrange(len(x)):
		for j in xrange(len(x[i])):
			for k in xrange(len(x[i][j])):
				total+=x[i][j][k]
	return total

if __name__ == '__main__':
	data_set = GoDataset("/home/justin/Programming/GoAI/MovePredictionCNN/data/input/train_samples.dat")
	x_inputs, targets = data_set.next_batch(500)
	print len(x_inputs), len(targets)
	for i in xrange(len(x_inputs)):
		print "sum: %d, move: %f" %(get_sum(x_inputs[i]), targets[i])