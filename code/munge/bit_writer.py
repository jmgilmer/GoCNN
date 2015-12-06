
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
	if bit_pos > 1:
		datafile.write(chr(this_byte))
		num_bytes += 1
	return num_bytes