import yacc
import sys
import os
import pprint
from lexer import tokens, lexer_global, lex_fun

output = []


# IMPORTANT: This entire code is written by me (R.N.Viswanadh) #

# Semantic Variables # 

temp_count = 0
string_count = 0
labels = 0
num_scopes = 0
function_count = 0
label_base = 'label'
temp_base = 'Temporarie'
scope_base = 'scope'
function_base = 'function'

offset = 0
shape = []

ST = {}
ST['addressDescriptor'] = {}
ST['main'] = {}
ST['main']['__name__'] = 'main'
ST['main']['__level__'] = 0
ST['main']['__variables__'] = [] 
ST['main']['__functions__'] = []

ST['scopes'] = [ST['main']]


def createTemp(varname, scope, type, data):
	global temp_count, temp_base
	new_place = temp_base+str(temp_count)
	temp_count += 1
	
	variable = {}
	variable['type'] = type
	variable['scope_level'] = scope['__level__']
	variable['place'] = new_place
	variable['data'] = data

	scope[varname] = variable
	scope['__variables__'].append(varname)
	ST['addressDescriptor'][new_place] = {'scope': scope, 'variable': varname}

	return new_place

def newTemp():
	global temp_count, temp_base
	new_place = temp_base+str(temp_count)
	temp_count += 1
	ST['addressDescriptor'][new_place] = {'scope': ST['scopes'][len(ST['scopes'])-1], 'variable': ''}	
	return new_place

def id_exists_already(identifier, type):
	scopes = ST['scopes']
	flag = False
	scope_count = 0
	for scope in reversed(scopes):
		scope_count += 1
		if type == 'variable':
			search_in = scope['__variables__']
		else:
			search_in = scope['__functions__']

		if identifier in search_in:
			flag = True
			return (flag, len(scopes)-scope_count)
	return (flag, -1)

def id_exists_currentScope(identifier):
	scope = ST['scopes'][len(ST['scopes'])-1]
	flag = False
	if identifier in scope['__variables__']:
		flag = True
	return flag

def createLabel():
	global labels, label_base
	label = label_base + str(labels)
	labels += 1
	if labels>100:
		print "INFINITE LOOP SOME WHERE ERROR"
		sys.exit()
	return label

def newScopeName():
	global num_scopes, scope_base
	new_scope_name = scope_base+str(num_scopes)
	num_scopes += 1
	return new_scope_name

def addScope():
	new_name = newScopeName()
	ST[new_name] = {}
	ST[new_name]['__name__'] = new_name
	ST[new_name]['__level__'] = len(ST['scopes'])
	ST[new_name]['__variables__'] = []
	ST[new_name]['__functions__'] = []
	ST['scopes'].append(ST[new_name])

def removeScope():
	ST['scopes'].pop()

def createTempforFunction(iden):
	global function_base, function_count
	new_place = function_base+str(function_count)
	function_count += 1

	curr_scope = ST['scopes'][len(ST['scopes'])-1]
	variable = {}
	variable['type'] = 'FUNCTION'
	variable['scope_level'] = curr_scope['__level__']
	variable['place'] = new_place

	curr_scope[iden] = variable

	curr_scope['__functions__'].append(iden)
	return new_place


def loop_and_print(obj, name):
	global offset
	elements = obj['elements']
	for temp_count in range(elements):
		processing_obj = obj['array'][temp_count]
		if processing_obj['elements']>1:
			loop_and_print(processing_obj, name)
		else:
			print "AI=, "+name+", "+str(offset)+", "+processing_obj['place']
			offset = offset + 4

def getshape(obj, arr):
	elements = obj['elements']
	arr.append(elements)
	processing_obj = obj['array'][0]
	if processing_obj['elements']>1:
		arr = getshape(processing_obj, arr)
	else:
		arr.append(1)
	return arr
	


#######################SEMANTIC RULES######################

def p_start(p):
	'''start : block
			 | statements'''
	

def p_block(p):
	'''block : LEFTBRACE blockmarker statements RIGHTBRACE'''
	removeScope()
	

def p_blockmarker(p):
	'''blockmarker : '''
	addScope()

def p_statements(p):
	'''statements : statement statements
				  | statement'''
	

def p_statement_semicolon(p):
	'''statement : assignment SEMICOLON
				 | declaration SEMICOLON 
				 | reassignment SEMICOLON 
				 | BREAK SEMICOLON
				 | CONTINUE SEMICOLON
				 | funcstmt SEMICOLON
				 | if
				 | ifelse
				 | whileloop
 				 | funcdecl
 				 | forloop
 				 | reassignmentarray SEMICOLON'''
	

def p_return_expression(p):
	'''statement : RETURN expression SEMICOLON'''
	print "push, "+p[2]['place']
	print "ret"

def p_statement_print(p):
	'''statement : CONSOLE DOT LOG LEFTPAREN printList RIGHTPAREN SEMICOLON'''
	for single_var in p[5]:
		print "print, "+single_var['place']

def p_printList(p):
	'''printList : expression COMMA printList'''
	single_var = {}
	single_var['type'] = p[1]['type']
	single_var['place'] = p[1]['place']
	p[0] = [ single_var ]+p[2]

def p_printList_base(p):
	'''printList : expression'''
	single_var = {}
	single_var['type'] = p[1]['type']
	single_var['place'] = p[1]['place']
	p[0] = [ single_var ]

	

################################
#########DECLARATION############
################################

def p_declaration(p):
	'''declaration : VAR declarationList'''
	current_scope = ST['scopes'][len(ST['scopes'])-1]
	for variable in p[2]:
		if variable not in current_scope['__variables__']:
			createTemp(varname = variable, scope = current_scope, type="UNDEFINED", data={})
		else:
			raise SyntaxError

	

def p_declarationList(p):
	'''declarationList : ID COMMA declarationList'''
	p[0] = [p[1]] + p[3]
	

def p_declarationList_base(p):
	'''declarationList : ID'''
	p[0] = [p[1]]
	



################################
#########ASSIGNMENT#############
################################

def p_assignment(p):
	'''assignment : VAR assignlist'''
	current_scope = ST['scopes'][len(ST['scopes'])-1]
	for variable in p[2]:
		if id_exists_currentScope(variable):
			print 'Redefined Variable'
			raise SyntaxError
		else:
			if variable['type']!='ARRAY':
				new_place = createTemp(varname = variable['name'], scope = current_scope, type = variable['type'], data={})
				print "=, "+new_place+", "+variable['place']
			else:
				new_place = createTemp(varname = variable['name'], scope = current_scope, type = variable['type'], data=variable['data'])

def p_assignlist(p):
	'''assignlist : ID EQ expression COMMA assignlist'''
	# print "assignlist"
	iden = {}
	iden['name'] = p[1]
	iden['type'] = p[3]['type']
	iden['place'] = p[3]['place']
	p[0] = [iden] + p[5]

def p_assignlist_base(p):
	'''assignlist : ID EQ expression'''
	# print "p_assignlist_base"
	iden = {}
	iden['name'] = p[1]
	iden['type'] = p[3]['type']
	iden['place'] = p[3]['place']
	p[0] = [iden]

def p_assignlist_array(p):
	'''assignlist : ID EQ array'''
	iden = {}
	iden['name'] = p[1]
	iden['type'] = 'ARRAY'
	iden['place'] = newTemp()
	iden['data'] = p[3]

	offset = 0
	shape = []
	arr = []

	arr = getshape(p[3], shape)
	iden['data']['shape'] = arr
	size = 4
	for element in arr:
		size = size * element

	print "array_def, "+p[1]+", "+str(size)
	loop_and_print(p[3], p[1])
	# pprint.pprint(arr) 
	p[0] = [iden]




##############################################
#################Reassignment#################
##############################################


def p_reassignment_arith(p):
	'''reassignment : ID EQ expression
					| ID PLUSEQ expression
					| ID MINUSEQ expression
					| ID INTOEQ expression
					| ID DIVEQ expression'''
	p[0] = {}
	flag, scope_level = id_exists_already(p[1], 'variable')
	if flag:
		dest = ST['scopes'][scope_level][p[1]]
		src = p[3]
		if p[2]!="=":
			if dest['type']!=src['type'] or dest['type']=='STRING':
				print "Reassignment types not matching"
				raise SyntaxError
		dest = dest['place']
		src = src['place']
		if p[2]=='=':
				print "=, "+dest+", "+src
		elif p[2]=='+=':
			print "+, "+dest+", "+src
		elif p[2]=='-=':
			print "-, "+dest+", "+src
		elif p[2]=='*=':
			print "*, "+dest+", "+src
		elif p[2]=='/=':
			print "/, "+dest+", "+src
		elif p[2]=='%=':
			print "%, "+dest+", "+src
		if scope_level!=len(ST['scopes'])-1:
			variable = {}
			variable['type'] = p[3]['type']
			variable['scope_level'] = len(ST['scopes'])-1
			variable['place'] = dest 
			ST['scopes'][len(ST['scopes'])-1]['__variables__'].append(p[1])
			ST['scopes'][len(ST['scopes'])-1][p[1]] = variable

	else:
		print p[1]+" identifier not definded"
		raise SyntaxError

def p_reassignment_incr(p):
	'''reassignment : ID INCR
					| ID DECR'''
	p[0] = {}
	flag, scope_level = id_exists_already(p[1], 'variable')
	if flag:
		dest = ST['scopes'][scope_level][p[1]]
		# if dest['type']!='NUMBER':
		# 	print "INCR or DECR is not possible since types are not matching"
		# 	raise SyntaxError
		temp = newTemp()
		print "B=, "+temp+", 1"
		
		if p[2]=='++':
			print "+, "+dest['place']+", "+temp
		elif p[2]=='--':
			print "-, "+dest['place']+", "+temp		
		if scope_level != len(ST['scopes'])-1:
			variable = {}
			variable['type'] = dest['type']
			variable['scope_level'] = len(ST['scopes'])-1
			variable['place'] = dest['place']
			ST['scopes'][len(ST['scopes'])-1]['__variables__'].append(p[1])
			ST['scopes'][len(ST['scopes'])-1][p[1]] = variable


def p_reassignment_shift(p):		
	'''reassignment	: ID LSHIFTEQ expression
					| ID RSHIFTEQ expression
					| ID URSHIFTEQ expression
					| ID ANDEQ expression
					| ID OREQ expression
					| ID XOREQ expression
					| ID MODEQ expression
					| LEFTPAREN reassignment RIGHTPAREN'''

# def p_switchexpression(p):
# 	'''switchexpression : expression'''
# 	current_scope = ST['scopes'][len(ST['scopes'])-1]
# 	current_scope['switchexpression'] = {}
# 	current_scope['switchexpression']['place'] = p[1]['place']
# 	current_scope['switchexpression']['type'] = p[1]['type']


# def p_switch_case(p):
# 	'''switchcase : SWITCH switchscope switchexpression LEFTBRACE case RIGHTBRACE'''

# def p_switchscope():
# 	'''switchscope : '''
# 	addscope()

# def p_case(p):
# 	'''case : CASE casemarker expression COLON statements BREAK endcasemarker case'''
	
# def p_case_base(p):
# 	'''case : CASE casemarker expression COLON statements BREAK endcasemarker'''


def p_casemarker(p):
	'''casemarker : '''
	addscope()

def p_endcasemarker(p):
	'''endcasemarker : '''
	removeScope()



def p_array(p):
	'''array : LEFTBRACKET arrayList RIGHTBRACKET'''
	p[0] = {}
	p[0]['type'] = 'ARRAY'
	p[0]['elements'] = p[2]['elements']
	p[0]['array'] = p[2]['array']


def p_arrayList_array(p):
	'''arrayList : array COMMA arrayList'''
	temp = {}
	temp['type'] = 'ARRAY'
	temp['elements'] = p[1]['elements']
	temp['array'] = p[1]['array']

	p[0] = {}
	p[0]['elements'] = 1 + p[3]['elements']
	p[0]['array'] = [temp] + p[3]['array']

def p_arrayList_base_array(p):
	'''arrayList : array'''
	temp = {}
	temp['type'] = 'ARRAY'
	temp['elements'] = p[1]['elements']
	temp['array'] = p[1]['array']

	p[0] = {}
	p[0]['elements'] = 1
	p[0]['array'] = [temp]

def p_arrayList_exp(p):
	'''arrayList : expression COMMA arrayList'''
	if p[1]['type']!='NUMBER':
		print "expression not a NUMBER, Check p_arrayList_base_exp"
		raise SyntaxError
	else:
		temp = {}
		temp['type'] = 'NUMBER'
		temp['elements'] = 1
		temp['place'] = p[1]['place']

		p[0] = {}
		p[0]['elements'] = 1 + p[3]['elements']
		p[0]['array'] = [temp] + p[3]['array']

def p_arrayList_base_exp(p):
	'''arrayList : expression'''
	if p[1]['type']!='NUMBER':
		print "expression not a NUMBER, Check p_arrayList_base_exp"
		raise SyntaxError
	else:
		temp = {}
		temp['type'] = 'NUMBER'
		temp['elements'] = 1
		temp['place'] = p[1]['place']

		p[0] = {}
		p[0]['array'] = [temp]
		p[0]['elements'] = 1


# Precedence of Operators
precedence = (
		('left', 'OR'),
		('left', 'AND'),
		('left', 'BINOR'),
		('left', 'BINXOR'),
		('left', 'BINAND'),
		('left', 'DOUBLEEQ', 'NOTEQUAL', 'STREQUAL', 'STRNEQUAL'),
		('left', 'LT', 'GT', 'LTE', 'GTE'),
		('left', 'LSHIFT', 'RSHIFT', 'URSHIFT'),
		('left', 'PLUS', 'MINUS'),
		('left', 'INTO', 'DIVIDE', 'MOD'),
		('right', 'NOT', 'BINNOT'),
		)

##################### Arithematic Operation ##########################
def p_expression_op(p):
	'''expression : expression PLUS expression
				  | expression MINUS expression
				  | expression INTO expression
				  | expression DIVIDE expression
				  | expression MOD expression'''
	new_place = newTemp()
	p[0] = {}
	p[0]['place'] = newTemp()
	if p[1]['type']!=p[3]['type']:
		print "types of arithematic expressions are not matching"
	else:
		p[0]['type'] = p[1]['type']
		print "=, "+p[0]['place']+", "+p[1]['place']
		print p[2]+", "+p[0]['place']+", "+p[3]['place']
	
	

###################### Group Expression #####################
def p_groupExp(p):
	'''expression : LEFTPAREN expression RIGHTPAREN'''
	p[0] = {}
	p[0]['type'] = p[2]['type']
	p[0]['place'] = p[2]['place']


##################### NOT of Expression ###################
def p_expression_not(p):	
	'''expression : NOT expression'''
	p[0] = {}

	if p[2]['type']=='BOOLEAN':
		p[0]['place'] = p[2]['place']
		t = newTemp()
		print "B=, "+t+", 1"
		print "+, "+p[0]['place']+", "+t
		print "B=, "+t+", 2"
		print "%, "+p[0]['place']+", "+t
	else:
		print "NOT Expression (Expression type is not BOOLEAN)"
		raise SyntaxError
	

def p_expression_binop(p):
	'''expression : expression BINAND expression
				  | expression BINOR expression
				  | expression BINXOR expression
				  | BINNOT expression'''
	

####################### Relational Op #####################
def p_expression_relop(p):
	'''expression : expression LT expression
				  | expression GT expression
				  | expression DOUBLEEQ expression
				  | expression NOTEQUAL expression
				  | expression LTE expression
				  | expression GTE expression'''

	p[0] = {}
	if True:
		p[0]['type'] = 'BOOLEAN'
		p[0]['place'] = newTemp()
		if p[2]=='<':
			op = 'jl'
		elif p[2]=='>':
			op = 'jg'
		elif p[2]=='==':
			op = 'je'
		elif p[2]=='!=':
			op = 'jne'
		elif p[2]=='<=':
			op = 'jle'
		elif p[2]=='>=':
			op = 'jge'
		
		label1 = createLabel()
		label2 = createLabel()
		label3 = createLabel()
		print "ifgoto, "+op+", "+p[1]['place']+", "+p[3]['place']+", "+label1
		print "goto, "+label2
		print "label, "+label1
		print "B=, "+p[0]['place']+", 1"
		print "goto, "+label3
		print "label, "+label2
		print "B=, "+p[0]['place']+", 0"
		print "label, "+label3

	# elif p[1]['type']==p[3]['type'] and p[1]['type']=='STRING':
	# 	p[0]['type'] = 'BOOLEAN'
		# p[0]['place'] = newTemp()
		# if p[2]=='<':
		# 	if p[3]['value']<p[1]['value']:
		# 		print "B=, "+p[0]['place']+", 1"
		# 	else:
		# 		print "B=, "+p[0]['place']+", 0"
		# elif p[2]=='>':
		# 	if p[3]['value']>p[1]['value']:
		# 		print "B=, "+p[0]['place']+", 1"
		# 	else:
		# 		print "B=, "+p[0]['place']+", 0"
		# elif p[2]=='==':
		# 	if p[3]['value']==p[1]['value']:
		# 		print "B=, "+p[0]['place']+", 1"
		# 	else:
		# 		print "B=, "+p[0]['place']+", 0"
		# elif p[2]=='!=':
		# 	if p[3]['value']!=p[1]['value']:
		# 		print "B=, "+p[0]['place']+", 1"
		# 	else:
		# 		print "B=, "+p[0]['place']+", 0"
		# elif p[2]=='<=':
		# 	if p[3]['value']<=p[1]['value']:
		# 		print "B=, "+p[0]['place']+", 1"
		# 	else:
		# 		print "B=, "+p[0]['place']+", 0"
		# elif p[2]=='>=':
		# 	if p[3]['value']<=p[1]['value']:
		# 		print "B=, "+p[0]['place']+", 1"
		# 	else:
		# 		print "B=, "+p[0]['place']+", 0"
	else:
		print "Type of expressions are not NUMBERS"
		raise SyntaxError


def p_expression_strop(p):
	'''expression : expression STREQUAL expression
				  | expression STRNEQUAL expression'''

######################## AND OR ########################

# WRONG IMPLEMENTATION

def p_expression_and_or(p):
	'''expression : expression AND expression
				  | expression OR expression'''
	p[0] = {}
	if p[1]['type']==p[3]['type'] and p[1]['type']=='BOOLEAN':
		p[0]['type'] = 'BOOLEAN'
		p[0]['place'] = p[1]['place']
		if p[2]=='&&':
			print "and, "+p[0]['place']+", "+p[3]['place']
		elif p[2]=='||':
			print "or, "+p[0]['place']+", "+p[3]['place']
		else:
			print "some thing wrong in expression and or"
			raise SyntaxError
	else:
		print "types not matching for and_or or types are not BOOLEAN"
		raise SyntaxError
	

def p_expression_shift(p):
	'''expression : expression LSHIFT expression
				  | expression RSHIFT expression
				  | expression URSHIFT expression'''
	


######################## EVAL ##########################
def p_expression_eval_undefined(p):
	'''expression : EVAL LEFTPAREN evalmarker statements evalendmarker RIGHTPAREN
				  | EVAL LEFTPAREN block RIGHTPAREN'''
	p[0] = {}
	p[0]['type'] = 'EVAL_UNDEFINED'
	p[0]['place'] = newTemp()
	p[0]['value'] = 0

def p_expression_eval_expression(p):
	'''expression : EVAL LEFTPAREN expression RIGHTPAREN'''
	p[0] = {}
	p[0]['type'] = p[3]['type']
	p[0]['place'] = newTemp()
	if p[0]['type'] in ['BOOLEAN', 'NUMBER', 'UNDEFINED']:
		print "=, "+p[0]['place']+', '+p[3]['place']
	else:
		print "check expression eval expression"

def p_evalmarker(p):
	'''evalmarker : '''
	addScope()

def p_evalendmarker(p):
	'''evalendmarker : '''
	removeScope()


############Expression Basic############

def p_expression_basic(p):
	'''expression : basicTypes'''
	p[0] = {}
	p[0]['type'] = p[1]['type']
	p[0]['place'] = newTemp()
	if p[0]['type'] in ['BOOLEAN', 'NUMBER', 'UNDEFINED']:
		print "B=, "+p[0]['place']+', '+str(p[1]['value'])
	else:
		"check the p_expression_basic definition"

############Expression ID###############

def p_expression_id(p):
	'''expression : ID'''
	p[0] = {}
	(flag, scope_index) = id_exists_already(p[1], 'variable')
	if flag:
		src = ST['scopes'][scope_index][p[1]]
		p[0]['type'] = src['type']
		p[0]['place'] = src['place']
		if p[0]['type'] in ['BOOLEAN', 'NUMBER', 'UNDEFINED']:
			t = 1
		else:
			"check the p_expression_id definition"
	else:
		print p[1]+" is NOT DEFINED"
		raise SyntaxError



def p_expression_type(p):
	'''expression : TYPEOF expression'''
	p[0] = {}
	p[0]['value'] = p[2]['type']
	p[0]['place'] = newTemp()
	p[0]['type'] = 'STRING'

def p_expression_functioncall_id(p):
	'''funcstmt : ID EQ functioncall'''

	p[0] = {}
	flag, scope_level = id_exists_already(p[1], 'variable')
	if flag:
		dest = ST['scopes'][scope_level][p[1]]
		src = p[3]
		if p[2]!="=":
			if dest['type']!=src['type']:
				print "Reassignment types not matching"
				raise SyntaxError
		dest = dest['place']
		src = src['place']
		scope_level = p[3]['scope_level']
		place = p[3]['place']
		temp = ST['scopes'][scope_level][p[1]]['place']
		print "call, "+ST['scopes'][scope_level][place]['place']+", "+temp

	else:
		print p[1]+" is not defined Already"



def p_expression_functioncall(p):
	'''funcstmt : functioncall'''
	scope_level = p[1]['scope_level']
	place = p[1]['place']
	print "call, "+ST['scopes'][scope_level][place]['place']

def p_expression_functioncall_varid(p):
	'''funcstmt : VAR ID EQ functioncall'''

	current_scope = ST['scopes'][len(ST['scopes'])-1]
	variable = p[2]
	if variable not in current_scope['__variables__']:
		createTemp(varname = variable, scope = current_scope, type="UNDEFINED", data={})
		scope_level = p[4]['scope_level']
		place = p[4]['place']
		print "call, "+ST['scopes'][scope_level][place]['place']+", "+current_scope[variable]['place']
	else:
		raise SyntaxError
	
	p[0] = {}
	p[0]['type'] = 'FUNCTIONCALL'
	p[0]['place'] = newTemp()
	print "pop, "+p[0]['place']


def p_expression_arraycall(p):
	'''expression : arrayCall'''
	val_in_addr = p[1]['val_in_addr']
	addr = p[1]['addr']

	p[0] = {}
	p[0]['type'] = 'NUMBER'
	p[0]['place'] = val_in_addr
	
	
	print "val, "+val_in_addr+", "+addr

def p_reassignment_array(p):
	'''reassignmentarray : arrayCall EQ expression'''
	addr = p[1]['addr']
	val_in_addr = p[1]['val_in_addr']
	print "updatearr, "+addr+", "+p[3]['place']

def p_arrayCall(p):
	'''arrayCall : ID reference'''
	flag, scope_level = id_exists_already(p[1], 'variable')
	if not flag:
		print "variable that you are referencing doesnot exist"
		raise SyntaxError
	else:
		array_ptr = ST['scopes'][scope_level][p[1]]
		# pprint.pprint(array_ptr)
		shape = array_ptr['data']['shape']
		if len(p[2])!=len(shape)-1:
			print "shape of the array and your referencing doesnot match"
			raise SyntaxError
		else:
			addr = newTemp()
			# address of p[1] to addr
			print "addr, "+addr+", "+p[1]
			temp_temp = newTemp()
			for ind in range(len(p[2])):
				t = ind+1
				multipland = 1
				while(t<len(shape)):
					multipland = multipland*shape[t]
					t = t + 1
				print "B=, "+temp_temp+", "+str(multipland*4)
				print "*, "+p[2][ind]['place']+", "+temp_temp

			for ind in range(len(p[2])):
				print "+, "+addr+", "+p[2][ind]['place']

			val_in_addr = newTemp()
			p[0] = {}
			p[0]['val_in_addr'] = val_in_addr
			p[0]['addr'] = addr
			p[0]['type'] = 'NUMBER'			
			p[0]['place'] = val_in_addr



def p_reference(p):
	'''reference : LEFTBRACKET expression RIGHTBRACKET reference'''
	if p[2]['type']!='NUMBER':
		print "Array index has to be number"
		raise SyntaxError
	else:
		temp = {}
		temp['type'] = p[2]['type']
		temp['place'] = p[2]['place']
		p[0] = [temp] + p[4]

def p_reference_base(p):
	'''reference : LEFTBRACKET expression RIGHTBRACKET'''
	if p[2]['type']!='NUMBER':
		print "Array index has to be number"
		raise SyntaxError
	else:
		temp = {}
		temp['type'] = p[2]['type']
		temp['place'] = p[2]['place']
		p[0] = [temp]


	



########################################
#############Basic Types################
########################################

def p_basicTypes_number(p):
	'''basicTypes : NUMBER'''
	p[0] = {}
	p[0]['type'] = 'NUMBER'
	p[0]['value'] = int(p[1])

def p_basicTypes_boolean(p):
	'''basicTypes : BOOLEAN'''
	if p[1] == 'true':
		value = 1
	else:
		value = 0
	p[0] = {}
	p[0]['type'] = 'BOOLEAN'
	p[0]['value'] = value

def p_basicTypes_string(p):
	'''basicTypes : STRING'''
	global string_count
	p[0] = {}
	p[0]['type'] = 'STRING'
	p[0]['value'] = p[1]
	p[0]['ref'] = '__string'+str(string_count)+'__'
	string_count += 1

def p_basicTypes_undefined(p):
	'''basicTypes : UNDEFINED'''
	p[0]['type'] = 'UNDEFINED'
	p[0]['value'] = 0
	

###########################################
################Function Call##############
###########################################


def p_functioncall(p):
	'''functioncall : ID LEFTPAREN argList RIGHTPAREN'''
	flag, scope_level = id_exists_already(p[1], 'function')	
	p[0] = {}
	if flag:
		for param in reversed(p[3]):
			print "param, "+param
		p[0]['scope_level'] = scope_level
		p[0]['place'] = p[1]
	else:
		print "No function named ", p[1], "Already defined"


def p_argList_expr(p):
	'''argList : expression'''
	p[0] = [p[1]['place']]

def p_argList(p):
	'''argList : expression COMMA argList'''
	p[0] = [p[1]['place']] + p[3]

def p_argList_base(p):
	'''argList : '''
	p[0] = []
	

###########################################
############## IF BLOCK ###################
###########################################


def p_if(p):
	'''if : IF expression ifelseblock block ifblockend'''

def p_ifblockend_marker(p):
	'''ifblockend : '''
	print "label, "+p[-2][1]

###########################################
############### IF - ELSE #################
###########################################

def p_ifelse(p):
	'''ifelse : IF expression ifelseblock block ELSE elseblock block elseblockend'''
	

def p_ifelseblock_marker(p):
	'''ifelseblock : '''
	label1 = createLabel()
	label2 = createLabel()
	label3 = createLabel()

	p[0] = [label1, label2, label3]

	t = newTemp()
	print "B=, "+t+", 1"
	print "ifgoto, je, "+p[-1]['place']+", "+t+", "+label1
	print "goto, "+label2
	print "label, "+label1

def p_elseblock_marker(p):
	'''elseblock : empty'''
	print "goto, "+p[-3][2]
	print "label, "+p[-3][1]

def p_elseblockend_marker(p):
	'''elseblockend : empty'''
	print "label, "+p[-5][2]


########################### cblock ########################

# def p_cblock(p):
# 	'''cblock : block 
# 			  | statement'''
# 	ST['scopes'].pop()
	

###################################################
#################### WHILE LOOP ###################
###################################################

def p_whileloop(p):
	'''whileloop : WHILE whileblockstart LEFTPAREN expression RIGHTPAREN exprcheck block whileblockend'''


def p_whileblockstart(p):
	'''whileblockstart : empty'''
	start = createLabel()
	end = createLabel()
	p[0] = [start, end]
	print "label, "+start

def p_exprcheck(p):
	'''exprcheck : empty'''
	t = newTemp()
	print "B=, "+t+", 1"
	print "ifgoto, jne, "+p[-2]['place']+", "+t+", "+p[-4][1]

def p_whileblockend(p):
	'''whileblockend : empty'''
	print "goto, "+p[-6][0]
	print "label, "+p[-6][1]

def p_forloop(p):
	'''forloop : FOR scope_marker LEFTPAREN initialization SEMICOLON forexpr_marker for_expr forcheck_marker SEMICOLON increment increment_marker RIGHTPAREN forblock endblock_marker'''

def p_scope_marker(p):
	'''scope_marker : '''
	addScope()

def p_forexpr_marker(p):
	'''forexpr_marker : '''
	p[0] = []
	label1 = createLabel()
	label2 = createLabel()
	label3 = createLabel()
	label4 = createLabel()
	p[0] = [label1, label2, label3, label4]
	print 'label, '+label1

def p_forcheck_marker(p):
	'''forcheck_marker : '''
	t = newTemp()
	print "B=, "+t+", 1"
	print "ifgoto, je, "+p[-1]['place']+", "+t+", "+p[-2][1]
	print "goto, "+p[-2][2]
	print "label, "+p[-2][3]

def p_increment_marker(p):
	'''increment_marker : '''
	print "goto, "+p[-5][0]
	print "label, "+p[-5][1]

def p_endblock_marker(p):
	'''endblock_marker : '''
	print "goto, "+p[-8][3]
	print "label, "+p[-8][2]
	removeScope()

def p_forblock(p):
	'''forblock : LEFTBRACE statements RIGHTBRACE'''


def p_initialization(p):
	'''initialization : assignment
					  | reinitialization'''

def p_reinitialization(p):	
	'''reinitialization : reassignment COMMA reinitialization
					  | reassignment'''

def p_for_expr(p):
	'''for_expr : expression'''
	p[0] = {}
	p[0]['place'] = p[1]['place']
	p[0]['type'] = p[1]['type']

def p_increment(p):
	'''increment : reassignment SEMICOLON increment
				 | reassignment'''
	

##################################################
############### FUNCTION DECLARATION #############
##################################################


def p_funcarghead(p):
	'''funcarghead : funcargList'''
	current_scope = ST['scopes'][len(ST['scopes'])-1]
	count = 1
	for variable in p[1]:
		if variable not in current_scope['__variables__']:
			new_place = createTemp(varname = variable, scope = current_scope, type="UNDEFINED", data = {})
			print "args, "+new_place+", "+str(count)
			count = count + 1
		else:
			raise SyntaxError


def p_funcargList(p):
	'''funcargList : ID COMMA funcargList'''
	p[0] = [p[1]] + p[3]


def p_funcargList_base(p):
	'''funcargList : ID'''
	p[0] = [p[1]]

def p_funcargList_empty(p):
	'''funcargList : '''
	p[0] = []


############### FUNCTION NORMAL ##################
def p_funcdecl_normal(p):
	'''funcdecl : FUNCTION ID funcscopedefnormal LEFTPAREN funcarghead RIGHTPAREN funblock endfunc'''
	removeScope()

def p_funcscopedefnormal(p):
	'''funcscopedefnormal : '''
	current_scope = ST['scopes'][len(ST['scopes'])-1]
	p[0] = {}
	if (p[-1] in current_scope['__functions__']) or (p[-1] in current_scope['__variables__']):
		print "Function or variable with this name Already definded in the current_scope"
		raise SyntaxError
	else:
		new_place = createTempforFunction(p[-1])
		label_jmp = createLabel()
		print "goto, "+label_jmp
		print "label, "+new_place
		p[0]['label'] = label_jmp
	addScope()


def p_endfunc(p):
	'''endfunc : empty'''
	print "ret"
	print "label, "+p[-5]['label']

############### VARIABLE FUNCTION DECL ###########

def p_funcdecl_vardecl(p):
	'''funcdecl	: VAR ID EQ FUNCTION funcscopedef LEFTPAREN funcarghead RIGHTPAREN funblock SEMICOLON endfuncdecl'''
	removeScope()

def p_funblock(p):
	'''funblock : LEFTBRACE statements RIGHTBRACE'''



def p_funcscopedef(p):
	'''funcscopedef : '''	
	current_scope = ST['scopes'][len(ST['scopes'])-1]
	if p[-3] in current_scope['__functions__'] or p[-3] in current_scope['__variables__']:
		print "Function or variable with this name Already definded in the current_scope"
		raise SyntaxError
	else:
		label_jmp = createLabel()
		new_place = createTempforFunction(p[-3])
		print "goto, "+label_jmp
		print "label, "+new_place
	addScope(p[-3])

def p_endfuncdecl(p):
	'''endfuncdecl : '''
	print "ret"
	print "label, "+p[-6]['label']

# Error rule for syntax errors
# def p_error_semicolon(p):
# 	'''statement : assignment 
# 				 | reassignment 
# 				 | BREAK
# 				 | CONTINUE
# 				 | RETURN expression
# 				 | CONSOLE DOT LOG LEFTPAREN expression RIGHTPAREN
# 				 | functioncall'''
# 	print "MAN!!! SEMICOLON is missing"

def p_empty(p):
	'''empty : '''

def p_error(p):
	print p
	print("YOU GOT A BUG IN YOUR INPUT, PLEASE CHECK")
	return



parser = yacc.yacc()

toks = []


def read_data(filename):
	script_dir = os.path.dirname(os.path.realpath('__file__'))
	if len(sys.argv)<2:
		print 'Give input file PLEASEEEEEEEE....'
		sys.exit()
	else:
		filename = script_dir+'/'+filename
		fp = open(filename, 'r')
		data = fp.read()
		lex_fun(data, toks)
		input = ""
		for tok in toks:
			if tok.type == 'LCOMMENT' or tok.type == 'BCOMMENT':
				continue
			input = input + str(tok.value) + " "
		return input		

if __name__ == '__main__':
	filename = sys.argv[1]
	data = read_data(filename)
	result = parser.parse(data, lexer=lexer_global)
	