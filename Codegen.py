import pprint
import sys
import copy


# IMPORTANT: This entire code is written by me (R.N.Viswanadh) #

#################################################
#################### GLOBALS ####################
#################################################

operators = ["=", "~", "!", "&", "+", "-", "*", "/", "%", "|", "^", "<<", ">>", "ifgoto", "&", "pointer", "address", "goto"]
non_operators = ['param', 'call', 'ret', 'label', 'print', 'pop', 'B=', 'args', 'updatearr']
rel_operators = ['jl', 'jg', 'je', 'jle', 'jge']



lang = operators + non_operators + rel_operators

src_types = ['AI=', 'push', 'print', 'param', 'pop']
dest_types = ['AR=', 'addr', 'B=', 'args']
both_types = ['=', '+', '-', '*', '/', '%', 'val', 'and', 'or', 'updatearr']
two_src_types = ['ifgoto']
not_cared = ['call', 'args']

arrays = []
leaders = []
basic_blocks = []
all_temps = []
var_descriptor = {}

register_descriptor = {}
registers = ['eax', 'ebx', 'ecx', 'edx', 'esi', 'edi']
for x in registers:
	temp_obj = {}
	temp_obj['state'] = "empty"
	temp_obj['temp'] = -1
	register_descriptor[x] = temp_obj

fp = open('log.txt', 'w')

#########################################################
####################### GET REG #########################
#########################################################

def free_reg():
	for reg in registers:
		if register_descriptor[reg]['state'] == 'filled':
			var = register_descriptor[reg]['temp']
			print "\tmovl %"+reg+", "+var
			var_descriptor[var]['location'] = 'memory'
			register_descriptor[reg]['state'] = 'empty'
	# print var_descriptor
	# print register_descriptor
	# for var in var_descriptor:
	# 	if var_descriptor[var]['location'] == 'register':
	# 		print "WRONG HERE"
	# print var_descriptor
	# print register_descriptor

#########################################################
####################### GET ONE REG #####################
#########################################################

def get_one_reg(not_wanted):
	for reg in registers:
		if reg not in not_wanted:
			if register_descriptor[reg]['state'] == 'empty':
				return reg
			else:
				temp = register_descriptor[reg]['temp']
				print "\tmovl %"+reg+", "+temp
				var_descriptor[temp]['location'] = 'memory'
				register_descriptor[reg]['state'] = 'empty'
				return reg



#########################################################
####################### GET REG #########################
#########################################################

def get_reg(temp, op, symbol_table, regs_allocated):
	if var_descriptor[temp]['location']=='register':
		reg = var_descriptor[temp]['register']
		# if register_descriptor[reg]['temp']!=temp:
		# 	# print "something very wrong "+reg+" "+temp
		return var_descriptor[temp]['register']


	for reg in register_descriptor:
		if register_descriptor[reg]['state']=='empty':
			register_descriptor[reg]['state'] = 'filled'
			register_descriptor[reg]['temp'] = temp

			var_descriptor[temp]['location'] = 'register'
			var_descriptor[temp]['register'] = reg
			print "\tmovl "+temp+", %"+reg
			
			return var_descriptor[temp]['register']

	################# heuristic ###################
	farthest_next_use = -1
	farthest_next_use_var = ''
	farthest_next_use_reg = 0
	# print "heuristic"
	for reg in register_descriptor:
		if reg in regs_allocated:
			continue
		exist_var = register_descriptor[reg]['temp']
		if (exist_var not in symbol_table) or (symbol_table[exist_var]['state']=='dead'):
			farthest_next_use_var = exist_var
			farthest_next_use_reg = reg
			break

		if farthest_next_use < symbol_table[exist_var]['next_use']:
			farthest_next_use = symbol_table[exist_var]['next_use']
			farthest_next_use_var = exist_var
			farthest_next_use_reg = reg
			

	print "\tmovl %"+farthest_next_use_reg+", "+farthest_next_use_var
	register_descriptor[reg]['temp'] = temp
	register_descriptor[reg]['state'] = 'filled'
	var_descriptor[farthest_next_use_var]['location'] = 'memory'
	var_descriptor[temp]['location'] = 'register'
	var_descriptor[temp]['register'] = farthest_next_use_reg
	print '\tmovl '+temp+", %"+farthest_next_use_reg

	return farthest_next_use_reg


#########################################################
#################### PRINT ASSEMBLY #####################
#########################################################

def print_assembly(basic_block, vars_in_each_line, list_symbol_tables, index):
	not_good_ops = ['/', '%', 'print', 'call', 'args']
	var_reg_map = {}
	op = basic_block[index][1]
	if op not in not_good_ops:
		regs_allocated = []
		# if op == '*':
		# 	print basic_block[index]
		for temp in vars_in_each_line[index]:
			reg = get_reg(temp, op, list_symbol_tables[index], regs_allocated)
			regs_allocated = [reg] + regs_allocated
			var_reg_map[temp] = reg
		if op in dest_types:
			dest = vars_in_each_line[index][0]
			dest_reg = var_reg_map[dest]
		
		elif op in src_types:
			src = vars_in_each_line[index][0]
			src_reg = var_reg_map[src]
		
		elif op in both_types:
			dest = vars_in_each_line[index][0]
			dest_reg = var_reg_map[dest]
			# print op
			src = vars_in_each_line[index][1]
			src_reg = var_reg_map[src]
		elif op in two_src_types:
			src1 = vars_in_each_line[index][0]
			src2 = vars_in_each_line[index][1]
			src1_reg = var_reg_map[src1]
			src2_reg = var_reg_map[src2]

		if op == 'B=':
			print "\tmovl $"+basic_block[index][3]+", %"+dest_reg
		elif op == '=':
			print "\tmovl %"+src_reg+", %"+dest_reg
		elif op == "+":
			print "\taddl %"+src_reg+", %"+dest_reg
		elif op == "*":
			print "\timul %"+src_reg+", %"+dest_reg
		elif op == "-":
			print "\tsubl %"+src_reg+", %"+dest_reg
		elif op == "goto":
			free_reg()
			print "\tjmp "+basic_block[index][2]
		elif op == "ifgoto":
			# print register_descriptor[src2_reg]
			# print register_descriptor[src1_reg]

			print "\tcmp %"+src2_reg+", %"+src1_reg
			free_reg()
			print "\t"+basic_block[index][2]+" "+basic_block[index][5]
		elif op == "and":
			print "\tandl %"+src_reg+", %"+dest_reg
		elif op == "or":
			print "\torl %"+src_reg+", %"+dest_reg
		elif op == "push":
			free_reg()
			print "\tmovl "+src+", %eax"
		elif op == "ret":
			print '\tret'
		elif op == "pop":
			if src_reg != 'eax':
				print "\tmovl %eax, %"+src_reg
		elif op == "label":
			print basic_block[index][2]+":"
			free_reg()
		elif op == "param":
			print "\tpushl %"+src_reg
		elif op == "AI=":
			dest_reg = get_one_reg([src_reg])
			print "\tmovl $("+basic_block[index][2]+"), %"+dest_reg
			print "\taddl $"+str(basic_block[index][3])+", %"+dest_reg
			print "\tmovl %"+src_reg+", (%"+dest_reg+")"

		elif op == "addr":
			print "\tmovl $("+basic_block[index][3]+"), %"+dest_reg

		elif op == "val":
			print "\tmovl (%"+src_reg+"), %"+dest_reg

		elif op == "updatearr":
			print "\tmovl %"+src_reg+", (%"+dest_reg+")"

		# elif op == "AR=":
		# 	src_reg = get_one_reg([dest_reg])
		# 	print "\tmovl $("+basic_block[index][2]+") %"+src_reg
		# 	print "\taddl $"+str(basic_block[index][3])+", "+src_reg
		# 	print "\tmovl (%"+src_reg+"), %"+dest_reg

		else:
			print "YOU HAVE NOT HANDLED THIS OP " + op
			raise SyntaxError

	else:
		if op == '/' or op == '%':
			dest = vars_in_each_line[index][0]
			src = vars_in_each_line[index][1]

			required_regs = ['eax', 'ebx', 'edx']
			free_reg()


			print "\tmovl $0, %edx"

			if var_descriptor[dest]['location'] == 'memory':
				print "\tmovl "+dest+", %eax"
				var_descriptor[dest]['location'] = 'register'
				
			else:
				dest_reg = var_descriptor[dest]['register']
				print "\tmovl %"+dest_reg+", %eax"
				register_descriptor[dest_reg]['state'] = 'empty'


			var_descriptor[dest]['register'] = 'eax'
			register_descriptor['eax']['state'] = 'filled'
			register_descriptor['eax']['temp'] = dest

			if var_descriptor[src]['location'] == 'memory':
				print "\tmovl "+src+", %ebx"
				var_descriptor[src]['location'] = 'register'
			else:
				src_reg = var_descriptor[src]['register']
				print "\tmovl %"+src_reg+", %ebx"
				register_descriptor[src_reg]['state'] = 'empty'


			var_descriptor[src]['location'] = 'register'
			var_descriptor[src]['register'] = 'ebx'
			register_descriptor['ebx']['state'] = 'filled'
			register_descriptor['ebx']['temp'] = src

			if op == '%':
				var_descriptor[dest]['location'] = 'register'
				var_descriptor[dest]['register'] = 'edx'
				register_descriptor['edx']['state'] = 'filled'
				register_descriptor['edx']['temp'] = dest

				register_descriptor['eax']['state'] = 'empty'

			elif op == '/':
				var_descriptor[dest]['location'] = 'register'
				var_descriptor[dest]['register'] = 'eax'
				register_descriptor['eax']['state'] = 'filled'
				register_descriptor['eax']['temp'] = dest

				register_descriptor['edx']['state'] = 'empty'

			print "\tdivl %ebx"

		elif op == "print":
			to_print = vars_in_each_line[index][0]
			if var_descriptor[to_print]['location'] == 'register':
				reg = var_descriptor[to_print]['register']
				print "\tmovl %"+reg+", "+to_print
				register_descriptor[reg]['state'] = 'empty'
				var_descriptor[to_print]['location'] = 'memory'
			free_reg()
			print '\tpushl '+to_print
			print '\tcall printIntNumber'
			print '\tpopl '+to_print

		elif op == "call":
			free_reg()
			print "\tcall "+basic_block[index][2]
			if len(vars_in_each_line[index])!=0:
				print "movl %eax, "+vars_in_each_line[index][0]
		
		elif op == "args":
			print "\tmovl "+str(4*int(basic_block[index][3]))+"(%esp), %eax"
			print "\tmovl %eax, "+basic_block[index][2]
		

				



#########################################################
################ RETURN CONTENT FUNCTION ################
#########################################################

def return_content(basic_block):
	all_vars_in_this_block = []
	vars_in_each_line = []
	# non_var = ['label', 'call', 'goto']
	# different_case = ['ifgoto']
	for line_code in basic_block:
		vars_in_this_line = []
		for word in line_code:
			# print word.find('Temporarie')
			if word.find('Temporarie')!=-1:
				vars_in_this_line.append(word)
				if word not in all_vars_in_this_block:
					all_vars_in_this_block.append(word)
		vars_in_each_line.append(vars_in_this_line)

	return (all_vars_in_this_block, vars_in_each_line)			



#########################################################
################### PROCESS FUNCTION ####################
#########################################################

def process(basic_block):
	(all_vars_in_this_block, vars_in_each_line)	= return_content(basic_block)

	# add temporaries to var_descriptor
	for temporary in all_vars_in_this_block:
		if temporary not in var_descriptor:
			temporary_obj = {}
			temporary_obj['location'] = 'memory'
			temporary_obj['register'] = -1
			var_descriptor[temporary] = temporary_obj

	################### SYMBOL TABLE ###################
	symbol_table = {}
	for temp in all_vars_in_this_block:
		temp_obj = {}
		temp_obj['state'] = 'dead'
		temp_obj['last_use'] = -1
		temp_obj['next_use'] = -1
		symbol_table[temp] = temp_obj
	if len(symbol_table)==0:
		list_symbol_tables = []
		for line_code in basic_block:
			list_symbol_tables.append(symbol_table)

		count = 0
		for line_code in basic_block:
			print_assembly(basic_block, vars_in_each_line, list_symbol_tables, count)
			count = count + 1
		# sys.exit()
		# uncomment it afterwards and handle this case
		# symbol_table = {}
		# for line_code in basic_block:
		# 	list_symbol_tables.append(symbol_table)
		# for line_code in basic_block:
		# 	line_index = basic_block.index(line_code)
		# 	print_assembly(basic_block, list_symbol_tables, vars_in_each_line, line_index)
		# return

	else:
		list_symbol_tables = [symbol_table]
		index = len(basic_block)-1
		for line_code in reversed(basic_block):
			symbol_table = copy.deepcopy(symbol_table)
			if len(vars_in_each_line[index]) == 0:
				list_symbol_tables = [symbol_table] + list_symbol_tables
				continue
			
			if line_code[1] in src_types:
				if(len(vars_in_each_line[index])!=1):
					print "something fishy, vars_in_this_line in src_types not equal to 1"
				else:
					source = vars_in_each_line[index][0]
					if symbol_table[source]['state']=='dead':
						symbol_table[source]['state'] = 'live'
						symbol_table[source]['last_use'] = index
						symbol_table[source]['next_use'] = index
					else:
						symbol_table[source]['next_use'] = index

			elif line_code[1] in dest_types:
				if(len(vars_in_each_line[index])!=1):
					print "something fishy, vars_in_this_line in dest_types not equal to 1"
				else:
					destination = vars_in_each_line[index][0]
					symbol_table[destination]['state'] = 'dead'
			elif line_code[1] in both_types:
				if(len(vars_in_each_line[index])!=2):
					print "something fishy, vars_in_this_line in both_types not equal to 2"
				else:
					destination = vars_in_each_line[index][0]
					symbol_table[destination]['state'] = 'dead'

					source = vars_in_each_line[index][1]
					if symbol_table[source]['state']=='dead':
						symbol_table[source]['state'] = 'live'
						symbol_table[source]['last_use'] = index
						symbol_table[source]['next_use'] = index
					else:
						symbol_table[source]['next_use'] = index
			elif line_code[1] in two_src_types:
				if len(vars_in_each_line[index])!=2:
					print "something fishy, vars_in_this_line in two_src_types not equal to 2"
				else:
					for source in vars_in_each_line[index]:
						if symbol_table[source]['state']=='dead':
							symbol_table[source]['state'] = 'live'
							symbol_table[source]['last_use'] = index
							symbol_table[source]['next_use'] = index
						else:
							symbol_table[source]['next_use'] = index
			else:
				if line_code[1] not in not_cared:
					print "NOT CARED FUNCTION "+line_code[1]
			index = index - 1
			list_symbol_tables = [symbol_table] + list_symbol_tables

		index = 0
		for line_code in basic_block:
			print_assembly(basic_block, vars_in_each_line, list_symbol_tables, index)
			index = index + 1



#########################################################
###################### MAIN BLOCK #######################
#########################################################

if __name__ == '__main__':
	outputfile = "asm_code.s"
	fp = open(outputfile, 'w')
	input_file_name = './' + sys.argv[1]
	with open(input_file_name, 'rb') as file:
		input_code = file.readlines()

	# forming splitted code
	splitted_code = []
	for input_line in input_code:
		temp = input_line.split(", ")
		temp[len(temp)-1] = temp[len(temp)-1][:-1]
		splitted_code.append(temp)
	

	# to_be_removed contains the lines which contains array defs.
	to_be_removed = []
	for line_code in splitted_code:
		if line_code[1] == 'array_def':
			temp = {}
			temp['array_name'] = line_code[2]
			temp['array_size'] = line_code[3]
			arrays.append(temp)
			to_be_removed.append(line_code)
	
	# removing the array defs from splitted code
	for x in to_be_removed:
		splitted_code.remove(x)
	
	# correcting the line numbers after removing array defs
	count = 1
	for line_code in splitted_code:
		line_code[0] = str(count)
		count = count + 1

	
	##################### finding leaders ######################

	temp_count = 2
	leaders.append(1)										# add line 1 to leaders
	for line_code in splitted_code[1:]:
		if line_code[1] == "ifgoto":						# next line of ifgoto
			if temp_count+1 <= len(splitted_code):
				leaders.append(temp_count+1)
		elif line_code[1] == "call":						# next line of call
			if temp_count+1 <= len(splitted_code):
				leaders.append(temp_count+1)
		elif line_code[1] == "label":						# line of label
			leaders.append(temp_count)
		elif line_code[1] == "ret":
			if temp_count+1 <= len(splitted_code):
				leaders.append(temp_count+1)
		temp_count = temp_count + 1

	# pprint.pprint(leaders)

	############### building basic blocks #####################
	temp_basic_block = [splitted_code[0]]
	count = 1
	for line_code in splitted_code[1:]:
		if count+1 in leaders:
			basic_blocks.append(temp_basic_block)
			temp_basic_block = [line_code]
		else:
			temp_basic_block.append(line_code)
		count = count + 1
	basic_blocks.append(temp_basic_block)

	# print "\tBasic Blocks"
	# pprint.pprint(basic_blocks)

	count = 0
	not_var_words = ['label', 'call']
	for basic_block in basic_blocks:
		for line_code in basic_block:
			for word in line_code:
				if word.find('Temporarie')!=-1:
					if word not in all_temps:
						all_temps.append(word)

	print '.section .text\n'
	print '\t.global _start\n'

	print '_start:'
	for basic_block in basic_blocks:
		process(basic_block)
		free_reg()
	a = 'end_label:\n\
	movl $1, %eax\n\
	movl $0, %ebx\n\
	int $0x80\n\
	'
	print ""+a
	a = 'printIntNumber:\n\
	movl 4(%esp), %ecx\n\
	cmpl $0, %ecx\n\
	jge positive_part\n\
	notl %ecx\n\
	inc %ecx\n\
	movl %ecx, %edi\n\
	movl $45, %eax\n\
	pushl   %eax\n\
	movl $4, %eax\n\
	movl $1, %ebx\n\
	movl %esp, %ecx\n\
	movl $1, %edx\n\
	int $0x80\n\
	popl %eax\n\
	movl %edi, %ecx\n\
positive_part:\n\
	movl %ecx, %eax\n\
	movl %esp, %esi\n\
iter_labl:\n\
	cdq\n\
	movl $10, %ebx\n\
	idivl %ebx\n\
	pushl %edx\n\
	cmpl $0, %eax\n\
	jne iter_labl\n\
	jmp print_num\n\
	\n\
print_num:\n\
	popl %edx\n\
	addl $48, %edx\n\
	pushl %edx\n\
	movl $4, %eax\n\
	movl $1, %ebx\n\
	movl %esp, %ecx\n\
	movl $1, %edx\n\
	int $0x80\n\
	popl %edx\n\
	cmp %esp, %esi\n\
	jne print_num\n\
	movl $4, %eax\n\
	movl $1, %ebx\n\
	movl $new, %ecx\n\
	movl $1, %edx\n\
	int $0x80\n\
	ret  \n\
EndPrintNum:\n'
	print a
	print '.section .data'
	for word in all_temps:
		print word+":"
		print "\t.long 0"
	for array in arrays:
		print array['array_name']+":"
		print "\t.space "+array['array_size']
	print 'new:'
	print '\t.ascii "\n"'
