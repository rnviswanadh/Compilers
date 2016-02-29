import yacc
import pprint
from lexer import tokens, lexer
from helper import dump 
def p_expression_plus(p):
	'expression : expression PLUS term'
	# print p[0], p[1], p[2]
	# p[0] = p[1] + p[3]
	pprint.pprint(p.slice)

def p_expression_minus(p):
	'expression : expression MINUS term'
	# p[0] = p[1] - p[3]
	pprint.pprint(p.slice)

def p_expression_term(p):
	'expression : term'
	# p[0] = p[1]
	pprint.pprint(p.slice)

def p_term_mod(p):
	'term : term MOD factor'
	# p[0] = p[1] % p[3]
	pprint.pprint(p.slice)

def p_term_factor(p):
	'term : factor'
	# p[0] = p[1]
	pprint.pprint(p.slice)

def p_factor_into(p):
	'factor : factor INTO fact'
	# p[0] = p[1] * p[3]
	pprint.pprint(p.slice)

def p_factor_divide(p):
	'factor : factor DIVIDE fact'
	# p[0] = p[1] / p[3]
	pprint.pprint(p.slice)

def p_factor_fact(p):
	'factor : fact'
	# p[0] = p[1]
	pprint.pprint(p.slice)

def p_fact_number(p):
	'fact : NUMBER'
	# p[0] = p[1]
	pprint.pprint(p.slice)

def p_fact_expr(p):
	'fact : LEFTPAREN expression RIGHTPAREN'
	# p[0] = p[2]
	pprint.pprint(p.slice)



 # Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")

parser = yacc.yacc()

while True:
	try:
		s = raw_input('calc > ')
	except EOFError:
		break
	if not s: continue
	# print 'HEY'
	result = parser.parse(s, lexer=lexer)
	print result

