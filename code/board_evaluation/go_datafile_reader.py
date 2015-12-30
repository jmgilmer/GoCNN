import numpy as np

def _read_sequence(datafile, num_bits):
	bits_read = 0
	bit_pos = 256
	this_byte = 0
	sequence = np.zeros(num_bits)
	while(bits_read < num_bits):
		if bit_pos >= 256:
			bit_pos = 1
			this_byte = ord(datafile.read(1))
			#print this_byte
			#if not this_byte:
			#	raise EOFError("At the end of the file")
		if this_byte&bit_pos != 0:
			sequence[bits_read] = 1.0
		else:
			sequence[bits_read] = 0.0
		bit_pos *=2
		bits_read +=1
	return sequence

class GoDatafileReader:
	def __init__(self, datafiles, board_size = 19):
		self.datafiles = datafiles
		assert(len(self.datafiles) != 0)
		self.num_epochs = 0
		self.index_of_file = 0
		self.board_size = board_size
		self.samples_read = 0
		self.current_file = open(self.datafiles[self.index_of_file], "rb")
	
	def open_next_file(self):
		self.index_of_file+=1
		if self.index_of_file >= len(self.datafiles):
			self.num_epochs+=1
			self.index_of_file = 0
		self.current_file.close()
		self.current_file = open(self.datafiles[self.index_of_file])

	#read the next feature cube from the binary file. Note this will increment the position in the file.
	#This function assumes the bytes 'GO' and the target bytes have already been read
	def _get_feature_cube(self):
		feature_cube = np.zeros((self.board_size,self.board_size,8))
		for i in xrange(self.board_size):
			for j in xrange(self.board_size):
				feature_byte = ord(self.current_file.read(1))
				for k in xrange(8):
					feature_cube[i][j][k] = ((feature_byte >> k) & 1)
				assert(((feature_byte  >> 7) &1) == 1)
		return feature_cube

	def read_sample(self):
		go_byte = self.current_file.read(2)
		if len(go_byte) == 0: #at the end of the file, open next one in queue
			self.open_next_file()
			go_byte = self.current_file.read(2)
		assert(go_byte == "GO")

		row = ord(self.current_file.read(1))
		col = ord(self.current_file.read(1))

		final_state = _read_sequence(self.current_file, self.board_size**2)
		#final_state = final_state.reshape((19,19))

		feature_cube = self._get_feature_cube()
		return final_state, (row, col), feature_cube

class BatchAggregator:
	def __init__(self, go_file_reader, mega_batch_size = 10000):
		self.go_file_reader = go_file_reader
		self.mega_batch_x = []
		self.mega_batch_y = []
		self.mega_batch_size = mega_batch_size
		self.index_in_mega_batch = mega_batch_size
	def init_mega_batch(self):
		for i in xrange(self.mega_batch_size):
			final_state, _, feature_cube = self.go_file_reader.read_sample()
			self.mega_batch_x.append(feature_cube)
			self.mega_batch_y.append(final_state)
		#jointly permute the features and the targets
		permutation = np.random.permutation(self.mega_batch_size)
		self.mega_batch_x = [self.mega_batch_x[i] for i in permutation]
		self.mega_batch_y = [self.mega_batch_y[i] for i in permutation]
		self.index_in_mega_batch = 0
	def get_batch(self, batch_size):
		if batch_size > self.mega_batch_size:
			raise ValueError('batch_size cannot be bigger than mega_batch_size')
		if self.index_in_mega_batch + batch_size > self.mega_batch_size:
			print "Got to end of mega batch, reinitializing..."
			self.init_mega_batch()
		x_list = self.mega_batch_x[self.index_in_mega_batch:self.index_in_mega_batch+batch_size]
		y_list = self.mega_batch_y[self.index_in_mega_batch:self.index_in_mega_batch+batch_size]
		self.index_in_mega_batch+=batch_size
		return x_list, y_list
