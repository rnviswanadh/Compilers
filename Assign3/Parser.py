import yacc
import pprint
from lexer import tokens, lexer
output = []
print len(tokens)
def p_start(p):
	'''start : block
			 | statements'''
	output.insert(0, p.slice)

def p_block(p):
	'''block : LEFTBRACE statements RIGHTBRACE
			 | LEFTBRACE RIGHTBRACE'''
	output.insert(0, p.slice)

def p_statements(p):
	'''statements : statement SEMICOLON statements
				  | statement'''
	output.insert(0, p.slice)

def p_statement_semicolon(p):
	'''statement : assignment SEMICOLON 
				 | reassignment SEMICOLON 
				 | BREAK SEMICOLON
				 | CONTINUE SEMICOLON
				 | RETURN expression SEMICOLON
				 | CONSOLE DOT LOG LEFTPAREN expression RIGHTPAREN SEMICOLON
				 | functioncall SEMICOLON 
				 | if
				 | ifelse
				 | whileloop
				 | forloop
 				 | funcdecl'''
	output.insert(0, p.slice)

def p_assignment(p):
	'''assignment : VAR assignlist'''
	output.insert(0, p.slice)

def p_assignlist(p):
	'''assignlist : ID EQ expression COMMA assignlist
				  | ID COMMA assignlist
				  | arraydecl COMMA assignlist
				  | ID EQ expression
				  | ID 
				  | arraydecl'''
	output.insert(0, p.slice)


def p_reassignment(p):
	'''reassignment : ID EQ expression
					| ID PLUSEQ expression
					| ID MINUSEQ expression
					| ID INTOEQ expression
					| ID DIVEQ expression
					| ID INCR
					| ID DECR
					| ID LSHIFTEQ expression
					| ID RSHIFTEQ expression
					| ID URSHIFTEQ expression
					| ID ANDEQ expression
					| ID OREQ expression
					| ID XOREQ expression
					| ID MODEQ expression
					| arraydecl'''
	output.insert(0, p.slice)

def p_arraydecl(p):
	'''arraydecl : ID EQ LEFTBRACKET arrayList RIGHTBRACKET'''

def p_arrayList(p):
	'''arrayList : expression COMMA arrayList
				 | expression
				 | '''

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

def p_expression_op(p):
	'''expression : expression PLUS expression
				  | expression MINUS expression
				  | expression INTO expression
				  | expression DIVIDE expression
				  | expression MOD expression'''
	output.insert(0, p.slice)

def p_groupExp(p):
	'''expression : LEFTPAREN expression RIGHTPAREN
				  | NOT expression'''
	output.insert(0, p.slice)

def p_expression_binop(p):
	'''expression : expression BINAND expression
				  | expression BINOR expression
				  | expression BINXOR expression
				  | expression BINNOT expression
				  | BINNOT expression'''
	output.insert(0, p.slice)

def p_expression_relop(p):
	'''expression : expression LT expression
				  | expression GT expression
				  | expression DOUBLEEQ expression
				  | expression NOTEQUAL expression
				  | expression LTE expression
				  | expression GTE expression
				  | expression STREQUAL expression
				  | expression STRNEQUAL expression
				  | expression AND expression
				  | expression OR expression'''
	output.insert(0, p.slice)

def p_expression_shift(p):
	'''expression : expression LSHIFT expression
				  | expression RSHIFT expression
				  | expression URSHIFT expression'''
	output.insert(0, p.slice)


def p_expression(p):
	'''expression : basicTypes
				  | functioncall
				  | arrayCall'''
	output.insert(0, p.slice)

def p_arrayCall(p):
	'''arrayCall : ID LEFTBRACKET expression RIGHTBRACKET'''
	output.insert(0, p.slice)

def p_basicTypes(p):
	'''basicTypes : NUMBER
				  | STRING
				  | ID'''
	output.insert(0, p.slice)

def p_functioncall(p):
	'''functioncall : ID LEFTPAREN argList RIGHTPAREN'''

def p_argList(p):
	'''argList : expression
			   | expression COMMA argList
			   | '''
	output.insert(0, p.slice)

def p_if(p):
	'''if : IF expression cblock '''
	output.insert(0, p.slice)

def p_ifelse(p):
	'''ifelse : IF expression cblock ELSE cblock
			  | IF expression cblock ELSE if
			  | IF expression cblock ELSE ifelse'''
	output.insert(0, p.slice)

def p_cblock(p):
	'''cblock : block 
			   | statement'''
	output.insert(0, p.slice)

def p_whileloop(p):
	'''whileloop : WHILE LEFTPAREN expression RIGHTPAREN cblock'''
	output.insert(0, p.slice)

def p_forloop(p):
	'''forloop : FOR LEFTPAREN initialization SEMICOLON expression SEMICOLON increment RIGHTPAREN cblock'''
	output.insert(0, p.slice)

def p_initialization(p):
	'''initialization : assignment SEMICOLON initialization
					  | reassignment SEMICOLON initialization
					  | assignment
					  | reassignment'''
	output.insert(0, p.slice)

def p_increment(p):
	'''increment : reassignment SEMICOLON increment
				 | reassignment'''
	output.insert(0, p.slice)

def p_funcdecl(p):
	'''funcdecl : FUNCTION ID LEFTPAREN argList RIGHTPAREN cblock
				| VAR ID EQ FUNCTION LEFTPAREN argList RIGHTPAREN cblock SEMICOLON'''
	output.insert(0, p.slice)




# Error rule for syntax errors
def p_error(p):
	print("YOU GOT A FUCKING BUG IN YOUR INPUT :P")

parser = yacc.yacc()

while True:
	try:
		s = raw_input('calc > ')
	except EOFError:
		break
	if not s: continue
	print s
	result = parser.parse(s, lexer=lexer)	
	# pprint.pprint(output)
	to_be_taken = output[0][0]
	line = [to_be_taken]
	print line
	temp_line = []
	lines = [list(line)]
	while len(output)!=0:
		out = output.pop(0)
		to_be_taken = out[0]
		out.pop(0)
		while len(line)!=0:
			item = line.pop()
			if item == to_be_taken:
				while len(out)!=0:
					line.append(out.pop())
				while len(temp_line)!=0:
					line.append(temp_line.pop())
				break
			else:
				temp_line.append(item)
		# pprint.pprint(line)
		lines.append(list(line))
	
	for line in lines:
		a = []
		for item in line:
			a.insert(0, item)
		output.append(list(a))
	pprint.pprint(output)

