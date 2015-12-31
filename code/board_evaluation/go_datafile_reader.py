import numpy as np
import random

#number of bytes in a single sample in a data file
#2 bytes = "GO" for data sync
#2 bytes for row, col of target move
#46 bytes for the final ownership (where the final board is binary and flattened into consecutive bits)
#  this gives ceiling(19*19 / 8) = 46 bytes
#19*19 bytes giving the features of the current board state, with piece liberties, ko position, and an all 1s bit pos
NUM_BYTES_IN_SAMPLE = 2 + 1 + 1 + 46 + 19*19

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

class RandomAccessFileReader:
	def __init__(self, datafiles, board_size = 19):
		self.datafiles = datafiles
		assert(len(self.datafiles) != 0)
		self.num_epochs = 0
		self.index_of_file = 0
		self.board_size = board_size
		self.samples_read = 0

		self.open_files = []
		print "Initializing pointers in %d datafiles, this may take a few minutes" %len(self.datafiles)
		for f in self.datafiles:
			file_obj = open(f, "rb")
			self._seek_random_place_in_file(file_obj)
			self.open_files.append(file_obj)

	def __del__(self):
		for f in self.open_files:
			f.close()

	#use resevoir sampling to pick a uniform random sample from the file of unknown number of samples
	@staticmethod
	def _seek_random_place_in_file(file_obj):
		file_pos = file_obj.tell()
		count = 1
		while True:
			temp_pos = file_obj.tell()
			sample_bytes = file_obj.read(NUM_BYTES_IN_SAMPLE)
			if len(sample_bytes) == 0:
				break
			assert(sample_bytes[:2] == "GO")
			if random.randint(1,count) == 1:
				file_pos = temp_pos
			count+=1
		file_obj.seek(file_pos,0)

	#read the next feature cube from the binary file. Note this will increment the position in the file.
	#This function assumes the bytes 'GO' and the target bytes have already been read
	def _get_feature_cube(self, file_obj):
		feature_cube = np.zeros((self.board_size,self.board_size,8))
		for i in xrange(self.board_size):
			for j in xrange(self.board_size):
				feature_byte = ord(file_obj.read(1))
				for k in xrange(8):
					feature_cube[i][j][k] = ((feature_byte >> k) & 1)
				assert(((feature_byte  >> 7) &1) == 1)
		return feature_cube

	def read_sample_from_random_file(self):
		file_to_read_from = random.choice(self.open_files)
		go_byte = file_to_read_from.read(2)
		if len(go_byte) == 0: #at the end of the file, open next one in queue
			#print "END OF FILE!!!!"
			file_to_read_from.seek(0,0)
			go_byte = file_to_read_from.read(2)
		assert(go_byte == "GO")

		row = ord(file_to_read_from.read(1))
		col = ord(file_to_read_from.read(1))

		final_state = _read_sequence(file_to_read_from, self.board_size**2)
		feature_cube = self._get_feature_cube(file_to_read_from)
		return final_state, (row, col), feature_cube

	def get_batch(self, batch_size = 50):
		final_states = []
		feature_cubes = []
		for i in xrange(batch_size):
			final_state, _, feature_cube = self.read_sample_from_random_file()
			final_states.append(final_state)
			feature_cubes.append(feature_cube)

		return feature_cubes, final_states

class GoDatafileReader:
	def __init__(self, datafiles, board_size = 19):
		self.datafiles = datafiles
		assert(len(self.datafiles) != 0)
		self.num_epochs = 0
		self.index_of_file = 0
		self.move_index = 0
		self.board_size = board_size
		self.samples_read = 0
		self.current_file = open(self.datafiles[self.index_of_file], "rb")
	
	def open_next_file(self):
		self.index_of_file+=1
		if self.index_of_file >= len(self.datafiles):
			self.num_epochs+=1
			self.index_of_file = 0
		self.current_file.close()
		self.current_file = open(self.datafiles[self.index_of_file], "rb")
		self.move_index = 0

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
			#print "END OF FILE!!!!"
			self.open_next_file()
			go_byte = self.current_file.read(2)
		assert(go_byte == "GO")

		row = ord(self.current_file.read(1))
		col = ord(self.current_file.read(1))

		final_state = _read_sequence(self.current_file, self.board_size**2)
		#final_state = final_state.reshape((19,19))

		feature_cube = self._get_feature_cube()
		self.move_index+=1
		return final_state, (row, col), feature_cube

class BatchAggregator:
	def __init__(self, go_file_reader, mega_batch_size = 10000):
		self.go_file_reader = go_file_reader
		self.mega_batch_x = []
		self.mega_batch_y = []
		self.mega_batch_size = mega_batch_size
		self.index_in_mega_batch = mega_batch_size

	def init_mega_batch(self):
		self.mega_batch_x = []
		self.mega_batch_y = []
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
			print "Epoch = %d" %self.go_file_reader.num_epochs
			self.init_mega_batch()
		x_list = self.mega_batch_x[self.index_in_mega_batch:self.index_in_mega_batch+batch_size]
		y_list = self.mega_batch_y[self.index_in_mega_batch:self.index_in_mega_batch+batch_size]
		self.index_in_mega_batch+=batch_size
		return x_list, y_list
