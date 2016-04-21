import sys
input_file_name = './' + sys.argv[1]
with open(input_file_name, 'rb') as file:
	input_code = file.readlines()
	count = 1
	for line in input_code:
		print str(count)+", "+line[:-1]
		count = count + 1