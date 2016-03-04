import sys
import yacc
import pprint
from lexer import tokens, lexer_global, lex_fun
# from helpers import preprocess



output = []
use_case = []
toks = []
NT = []				# Non Terminals

def p_start(p):
	'''start : block
			 | statements'''
	output.insert(0, p.slice)
	use_case.insert(0, list(p.slice))

def p_block(p):
	'''block : LEFTBRACE statements RIGHTBRACE
			 | LEFTBRACE RIGHTBRACE'''
	output.insert(0, p.slice)
	use_case.insert(0, list(p.slice))

def p_statements(p):
	'''statements : statement statements
				  | statement'''
	output.insert(0, p.slice)
	use_case.insert(0, list(p.slice))

def p_statement_semicolon(p):
	'''statement : assignment SEMICOLON 
				 | reassignment SEMICOLON 
				 | BREAK SEMICOLON
				 | CONTINUE SEMICOLON
				 | RETURN expression SEMICOLON
				 | expression SEMICOLON
				 | CONSOLE DOT LOG LEFTPAREN expression RIGHTPAREN SEMICOLON
				 | functioncall SEMICOLON 
				 | if
				 | ifelse
				 | whileloop
				 | forloop
 				 | funcdecl'''
	output.insert(0, p.slice)
	use_case.insert(0, list(p.slice))


def p_assignment(p):
	'''assignment : VAR assignlist
				  | LEFTPAREN assignment RIGHTPAREN'''
	output.insert(0, p.slice)
	use_case.insert(0, list(p.slice))

def p_assignlist(p):
	'''assignlist : ID EQ expression COMMA assignlist
				  | ID COMMA assignlist
				  | arraydecl COMMA assignlist
				  | ID EQ expression
				  | ID 
				  | arraydecl'''
	output.insert(0, p.slice)
	use_case.insert(0, list(p.slice))


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
					| arraydecl
					| LEFTPAREN reassignment RIGHTPAREN'''
	output.insert(0, p.slice)
	use_case.insert(0, list(p.slice))

def p_arraydecl(p):
	'''arraydecl : ID EQ LEFTBRACKET arrayList RIGHTBRACKET'''
	output.insert(0, p.slice)
	use_case.insert(0, list(p.slice))

def p_arrayList(p):
	'''arrayList : expression COMMA arrayList
				 | arraydecl COMMA arrayList
				 | arraydecl
				 | expression
				 | '''
	output.insert(0, p.slice)
	use_case.insert(0, list(p.slice))

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
		('right', 'EXPO'),
		('right', 'NOT', 'BINNOT'),
		)

def p_expression_gen(p):
	'''expression : EVAL LEFTPAREN statements RIGHTPAREN
				  | EVAL LEFTPAREN block RIGHTPAREN'''
	output.insert(0, p.slice)
	use_case.insert(0, list(p.slice))

def p_expression_op(p):
	'''expression : expression PLUS expression
				  | expression MINUS expression
				  | expression INTO expression
				  | expression DIVIDE expression
				  | expression MOD expression
				  | expression EXPO expression'''
	output.insert(0, p.slice)
	use_case.insert(0, list(p.slice))

def p_groupExp(p):
	'''expression : LEFTPAREN expression RIGHTPAREN
				  | NOT expression'''
	output.insert(0, p.slice)
	use_case.insert(0, list(p.slice))

def p_expression_binop(p):
	'''expression : expression BINAND expression
				  | expression BINOR expression
				  | expression BINXOR expression
				  | BINNOT expression'''
	output.insert(0, p.slice)
	use_case.insert(0, list(p.slice))

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
	use_case.insert(0, list(p.slice))

def p_expression_shift(p):
	'''expression : expression LSHIFT expression
				  | expression RSHIFT expression
				  | expression URSHIFT expression'''
	output.insert(0, p.slice)
	use_case.insert(0, list(p.slice))


def p_expression(p):
	'''expression : basicTypes
				  | functioncall
				  | arrayCall
				  | TYPEOF expression'''
	output.insert(0, p.slice)
	use_case.insert(0, list(p.slice))

def p_arrayCall(p):
	'''arrayCall : ID LEFTBRACKET expression RIGHTBRACKET'''
	output.insert(0, p.slice)
	use_case.insert(0, list(p.slice))

def p_basicTypes(p):
	'''basicTypes : NUMBER
				  | STRING
				  | ID
				  | UNDEFINED'''
	output.insert(0, p.slice)
	use_case.insert(0, list(p.slice))

def p_functioncall(p):
	'''functioncall : ID LEFTPAREN argList RIGHTPAREN'''
	output.insert(0, p.slice)
	use_case.insert(0, list(p.slice))

def p_argList(p):
	'''argList : expression
			   | expression COMMA argList
			   | '''
	output.insert(0, p.slice)
	use_case.insert(0, list(p.slice))

def p_if(p):
	'''if : IF expression cblock '''
	output.insert(0, p.slice)
	use_case.insert(0, list(p.slice))

def p_ifelse(p):
	'''ifelse : IF expression cblock ELSE cblock
			  | IF expression cblock ELSE if
			  | IF expression cblock ELSE ifelse'''
	output.insert(0, p.slice)
	use_case.insert(0, list(p.slice))

def p_cblock(p):
	'''cblock : block 
			   | statement'''
	output.insert(0, p.slice)
	use_case.insert(0, list(p.slice))

def p_whileloop(p):
	'''whileloop : WHILE LEFTPAREN expression RIGHTPAREN cblock'''
	output.insert(0, p.slice)
	use_case.insert(0, list(p.slice))

def p_forloop(p):
	'''forloop : FOR LEFTPAREN initialization SEMICOLON expression SEMICOLON increment RIGHTPAREN cblock'''
	output.insert(0, p.slice)
	use_case.insert(0, list(p.slice))

def p_initialization(p):
	'''initialization : assignment SEMICOLON initialization
					  | reassignment SEMICOLON initialization
					  | assignment
					  | reassignment'''
	output.insert(0, p.slice)
	use_case.insert(0, list(p.slice))

def p_increment(p):
	'''increment : reassignment SEMICOLON increment
				 | reassignment'''
	output.insert(0, p.slice)
	use_case.insert(0, list(p.slice))

def p_funcdecl(p):
	'''funcdecl : FUNCTION ID LEFTPAREN argList RIGHTPAREN cblock
				| VAR ID EQ FUNCTION LEFTPAREN argList RIGHTPAREN cblock SEMICOLON'''
	output.insert(0, p.slice)
	use_case.insert(0, list(p.slice))




# Error rule for syntax errors
def p_error_semicolon(p):
	'''statement : assignment 
				 | reassignment 
				 | BREAK
				 | CONTINUE
				 | expression
				 | CONSOLE DOT LOG LEFTPAREN expression RIGHTPAREN
				 | functioncall'''
	print "MAN!!! SEMICOLON is missing"

def p_error(p):
	print("YOU GOT A BUG IN YOUR INPUT, PLEASE CHECK")
	return

parser = yacc.yacc()

def get_token():
	tok = toks.pop(0)
	print toks
	return tok

if __name__ == '__main__':
	if len(sys.argv)<2:
		print 'Give input file PLEASEEEEEEEE....'
	a = './' + sys.argv[1]
	fp = './' + sys.argv[1][:len(sys.argv[1])-2]+'html'
	# print fp
	f = open(a, 'r')
	fp = open(fp, 'wb')
	data = f.read()
	lex_fun(data, toks)
	input = ""
	for tok in toks:
		input = input + " " + str(tok.value)
	# print input
	lexer_global.input(input)
	while True:
		tok = lexer_global.token()
		if not tok: 
			break 
		# else:
		# 	print tok

	result = parser.parse(input, lexer=lexer_global)
	# use_case1 = list(use_case)
	to_be_taken = output[0][0]
	if to_be_taken not in NT:
		NT.append(to_be_taken)

	line = [to_be_taken]
	temp_line = []
	lines = [list(line)]
	while len(output)!=0:
		out = output.pop(0)
		to_be_taken = out[0]
		if to_be_taken not in NT:
			NT.append(to_be_taken)
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
	# print NT
	for i in range(0, len(output)):
		for j in range(0, len(output[i])):
			if output[i][j] not in NT:
				output[i][j] = output[i][j].value
	print_output = []
	# print output
	# print len(output), len(use_case)
	for out in output:
		# print out
		if output.index(out)==len(output)-1:
			break
		out_reverse = []
		for a in out:
			out_reverse.insert(0, a)
		p = []
		t = use_case[output.index(out)][0]
		for a in out_reverse:
			if a==t:
				b = out.index(a)
				p.insert(0,b)
				p.append(len(use_case[output.index(out)])-1)
				# print p
				break
		print_output.append(list(p))
	
	fp.write('''<!DOCTYPE html>
				<html>
				<head>
					<title>Right Most Derivation</title>
					<style type="text/css">
						.expands{
							color: #5714CE;
						}
						
						td{
							background: white;
						}
					</style>
				</head>
				<body>''')
	fp.write('<table>')
	for out in output:
		if output.index(out)==len(output)-1:
			break
		fp.write('<tr>')
		for a in out:
			p = print_output[output.index(out)][0]
			if out.index(a)==p:
				if output.index(out)!=0:
					l = print_output[output.index(out)-1]
					if p>=l[0] and p<l[0]+l[1]:
						fp.write('<td class="expands expanded">'+str(a)+'</td>')
					else:
						fp.write('<td class="expands">'+str(a)+'</td>')
				else:
					fp.write('<td class="expands expanded">'+str(a)+'</td>')
			else:
				if output.index(out)!=0:
					l = print_output[output.index(out)-1]
					if output.index(out)>=l[0] and output.index(out)<l[0]+l[1]:
						fp.write('<td class="expanded">'+str(a)+'</td>')
					else:
						fp.write('<td>'+str(a)+'</td>')
		fp.write('</tr>')
	p = print_output[len(print_output)-1]
	d = output[len(output)-1]
	for a in d:
		if d.index(a)>=p[0] and d.index(a)<p[0]+p[1]:
			fp.write('<td class="expanded">'+str(a)+'</td>')
		else:
			fp.write('<td>'+str(a)+'</td>')
	fp.write('</table></body>')
	fp.write('</html>')
