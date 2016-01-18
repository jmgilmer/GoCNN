
import numpy as np

def write_sequence(sequence, datafile):
	bit_pos = 1
	this_byte = 0
	num_bytes = 0
	for bit in sequence:
		if bit == 1:
			this_byte = this_byte | bit_pos
		bit_pos *= 2
		if bit_pos >= 256:
			bit_pos = 1
			datafile.write(chr(this_byte))
			num_bytes += 1
			this_byte = 0
	if bit_pos > 1:
		datafile.write(chr(this_byte))
		num_bytes += 1
	return num_bytes

def read_sequence(datafile, num_bits):
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

