#!/usr/bin/python
from ply import yacc
from JSlexer import tokens, lexer, debug

from helpers import symbolTable as SymbolTable
from helpers import threeAddressCode as ThreeAddressCode

########################################
############# STATEMENTS ###############
########################################
def p_start(p):
    '''start : block
             | statements'''

    # Any remaining breaks and continues need to be purged
    TAC.noop(p[1]['loopEndList'])
    TAC.noop(p[1]['loopBeginList'])

    # Here we have to have statements so that we can return back to the calling function
    TAC.emit('', '' , -1, 'HALT')

    # Main has zero parameters
    ST.addAttributeToCurrentScope('numParam', 0)

    # Now delete the main scope
    ST.deleteScope('main')

    # Emit code
    p[0] = {}

def p_block(p):
    'block : SEP_OPEN_BRACE statements SEP_CLOSE_BRACE'

    # Emit code
    p[0] = {}

    # For break statement
    p[0]['loopEndList'] = p[2].get('loopEndList', [])
    p[0]['loopBeginList'] = p[2].get('loopBeginList', [])

def p_block_empty(p):
    'block : SEP_OPEN_BRACE empty SEP_CLOSE_BRACE'

    # Emit code
    p[0] = {}

    # Empty blocks are not allowed, this points out this mistake
    debug.printError('Empty blocks are not allowed')
    raise SyntaxError

def p_statments(p):
    '''statements : statement statements
                  | statement M_statements'''

    p[0] = {}

    # break statements and continue statements need to pushed up
    p[0]['loopEndList'] = TAC.merge(p[1].get('loopEndList', []), p[2].get('loopEndList', []))
    p[0]['loopBeginList'] = TAC.merge(p[1].get('loopBeginList', []), p[2].get('loopBeginList', []))

# The set of statements that require a semi-colon termination
def p_statment(p):
    '''statement : assignment M_quad SEP_SEMICOLON
                 | declaration M_quad SEP_SEMICOLON
                 | breakStatement M_quad SEP_SEMICOLON
                 | continueStatement M_quad SEP_SEMICOLON
                 | returnStatement M_quad SEP_SEMICOLON
                 | printStatement M_quad SEP_SEMICOLON
                 | functionCall M_quad SEP_SEMICOLON'''

    # the empty semicolon rules introduces a shift reduce conflict
    # Emit code
    p[0] = {}

    # Statements waiting for the next list get backpatched
    nextList = p[1].get('nextList', [])
    TAC.backPatch(nextList, p[2]['quad'])

    # break statements and continue statements need to pushed up
    p[0]['loopEndList'] = p[1].get('loopEndList', [])
    p[0]['loopBeginList'] = p[1].get('loopBeginList', [])

# The set of statements that don't require a semi-colon termination
def p_statement_no_semicolon(p):
    '''statement : ifThen M_quad
                 | ifThenElse M_quad
                 | whileStatement M_quad
                 | functionStatement M_quad'''

    # Emit code
    p[0] = {}

    # Statements waiting for the next list get backpatched
    nextList = p[1].get('nextList', [])
    TAC.backPatch(nextList, p[2]['quad'])

    # break statements and continue statements need to pushed up
    p[0]['loopEndList'] = p[1].get('loopEndList', [])
    p[0]['loopBeginList'] = p[1].get('loopBeginList', [])

# To notify the user of a missing semicolon
def p_statement_error(p):
    '''statement : assignment M_quad
                 | breakStatement M_quad
                 | returnStatement M_quad
                 | continueStatement M_quad
                 | printStatement M_quad
                 | functionCall M_quad'''

    # Emit code
    p[0] = {}

    # Statements waiting for the next list get backpatched
    nextList = p[1].get('nextList', [])
    TAC.backPatch(nextList, p[2]['quad'])

    # break statements and continue statements need to pushed up
    p[0]['loopEndList'] = p[1].get('loopEndList', [])
    p[0]['loopBeginList'] = p[1].get('loopBeginList', [])

    # Raise an error
    debug.printError('Semicolon missing')
    raise SyntaxError

# Marker to mark the nextQuad value
def p_mark_quad(p):
    'M_quad : empty'

    p[0] = { 'quad' : TAC.getNextQuad()}

# Marker for blanck statements
def p_mark_statements(p):
    'M_statements : empty'

    p[0] = {}

########################################
############# DECLARATION ##############
########################################
def p_declaration(p):
    'declaration : VAR decList'

    # Add identifiers to local scope
    for identifierName in p[2]:
        # Put the identifier into the symbolTable
        identifierEntry = ST.existsInCurrentScope(identifierName)
        if identifierEntry == False:
            ST.addIdentifier(identifierName, 'UNDEFINED')

            # Create a temporary for the current scope
            displayValue, offset = ST.getAttribute(identifierName, 'scopeLevel'), ST.getAttribute(identifierName, 'offset')
            place = ST.newTemp((displayValue, offset), variable=identifierName)
            ST.addAttribute(identifierName, ST.getCurrentScope(), place)
        else:
            debug.printError('Redefined Variable "%s"' %identifierName)
            raise SyntaxError

        debug.printStatement("Declaration '%s'" %identifierName)

    # Type rules
    p[0] = {}

def p_decList(p):
    'decList : IDENTIFIER SEP_COMMA decList'

    p[0] = [ p[1] ] + p[3]

def p_decList_base(p):
    'decList : IDENTIFIER'

    p[0] = [p[1]]

def p_decList_empty(p):
    'decList : empty'''

    p[0] = [ ]

########################################
############# ASSIGNMENT ###############
########################################
def p_assignment(p):
    'assignment : VAR assignList'

    # In case the var is not present
    p[0] = { 'type' : 'VOID' }

    # Now we add all of these statements
    for identifier in p[2]:
        if not ST.existsInCurrentScope(identifier['name']):
            # Store information about the identifier
            ST.addIdentifier(identifier['name'], identifier['type'])

            # This is a new variable, so we link the temporary to our variable
            displayValue, offset = ST.getAttribute(identifier['name'], 'scopeLevel'), ST.getAttribute(identifier['name'], 'offset')
            ST.changeMemoryLocationOfTemp(identifier['place'], (displayValue, offset), variable=identifier['name'])
            ST.addAttribute(identifier['name'], ST.getCurrentScope(), identifier['place'])
            ST.addAttribute(identifier['name'], 'reference', identifier['reference'])

            # print the name of the statement
            debug.printStatement("ASSIGNMENT of %s" %identifier['name'])
        else:
            debug.printError('Redefined Variable "%s"' %identifier['name'])
            raise SyntaxError

def p_assignList(p):
    'assignList : IDENTIFIER OP_ASSIGNMENT expression SEP_COMMA assignList'

    # Create an identifier instance to pass
    identifier = {}
    identifier['name'] = p[1]
    identifier['type'] = p[3]['type']
    identifier['place'] = p[3]['place']
    identifier['reference'] = p[3].get('reference')

    p[0] = [identifier] + p[5]

def p_assignList_base(p):
    'assignList : IDENTIFIER OP_ASSIGNMENT expression'

    identifier = {}
    identifier['name'] = p[1]
    identifier['type'] = p[3]['type']
    identifier['place'] = p[3]['place']
    identifier['reference'] = p[3].get('reference')

    p[0] = [identifier]

def p_assignment_redefinition(p):
    'assignment : IDENTIFIER OP_ASSIGNMENT expression'

    # To store information
    p[0] = {}

    identifierEntry = ST.exists(p[1])
    if identifierEntry == True:
        ST.addAttribute(p[1], 'type', p[3]['type'])

        # Check if the function is in the current scope or parent one
        if ST.existsInCurrentScope(p[1]):
            place = ST.getAttribute(p[1], ST.getCurrentScope())
        else:
            # store the address into the address descriptor
            displayValue, offset = ST.getAttribute(p[1], 'scopeLevel'), ST.getAttribute(p[1], 'offset')
            place = ST.newTemp((displayValue, offset), variable=p[1])
            ST.addAttribute(p[1], ST.getCurrentScope(), place)

        TAC.emit(place, p[3]['place'], '', '=')
    else:
        debug.printError('Undefined Variable "%s"' %p[1])
        raise SyntaxError

    # print the name of the statement
    debug.printStatement("ASSIGNMENT of %s" %p[1])

########################################
############## FUNCTIONS ###############
########################################
def p_functionStatement(p):
    '''functionStatement : FUNCTION IDENTIFIER M_scope SEP_OPEN_PARENTHESIS argList SEP_CLOSE_PARENTHESIS M_insertArgs block
                          | FUNCTION M_anonName M_scope SEP_OPEN_PARENTHESIS argList SEP_CLOSE_PARENTHESIS M_insertArgs block'''

    # Any remaining breaks and continues need to be purged
    TAC.noop(p[8]['loopEndList'])
    TAC.noop(p[8]['loopBeginList'])

    # Here we have to have statements so that we can return back to the calling function
    TAC.emit('', '' , '', 'JUMPBACK')

    # print the name of the statement
    functionName = p[3]['reference']
    ST.deleteScope(functionName)

    # Type rules
    p[0] = { 'type' : 'FUNCTION', 'reference': functionName }

def p_scope(p):
    'M_scope : empty'

    p[0] = {}

    # Name the function
    p[0]['reference'] = ST.nameAnon()

    # Now add the identifier as a function reference
    if p[-1] != None: # Check for anon function
        # Check if the function exists or not
        if ST.existsInCurrentScope(p[-1]):
            debug.printError("Redefinition of function '%s'" %p[-1])
            raise SyntaxError
        else:
            # Print to console
            debug.printStatementBlock("Definition of function '%s'" %p[-1])

            # Create a new variable to hold the function
            ST.addIdentifier(p[-1], 'FUNCTION')

            # Create a new temporary for the function and store it in the addressList
            displayValue, offset = ST.getAttribute(p[-1], 'scopeLevel'), ST.getAttribute(p[-1], 'offset')
            place = ST.newTemp((displayValue, offset), variable=p[-1])
            ST.addAttribute(p[-1], ST.getCurrentScope(), place)
            ST.addAttribute(p[-1], 'reference', p[0]['reference'])

            # Emit the location of the function reference
            TAC.emit(place, p[0]['reference'], '', '=REF')
    else:
        # Print to console
        debug.printStatementBlock('Function Definition "%s"' %p[0]['reference'])

    # Create a function scope
    ST.addScope(p[0]['reference'])
    TAC.createFunctionCode(p[0]['reference'])

def p_anonName(p):
    'M_anonName : empty'

    p[0] = None

def p_argList(p):
    'argList : hint SEP_COMMA argList'

    p[0] = [ p[1] ] + p[3]

def p_argList_base(p):
    'argList : hint'

    p[0] = [p[1]]

def p_argList_empty(p):
    'argList : empty'''

    p[0] = [ ]

def p_hint(p):
    '''hint : IDENTIFIER OP_HINT HINT_NUMBER
            | IDENTIFIER OP_HINT HINT_CALLBACK
            | IDENTIFIER OP_HINT HINT_STRING
            | IDENTIFIER OP_HINT HINT_ARRAY
            | IDENTIFIER OP_HINT HINT_BOOLEAN'''

    p[0] = {'name': p[1] }

    # According to the hint assign a type to the identifier
    if p[3] == 'callback':
        p[0]['type'] = 'CALLBACK'
    elif p[3] == 'num':
        p[0]['type'] = 'NUMBER'
    elif p[3] == 'bool':
        p[0]['type'] = 'BOOLEAN'
    elif p[3] == 'string':
        p[0]['type'] = 'STRING'
    else:
        p[0]['type'] = 'ARRAY'

def p_hint_error(p):
    'hint : IDENTIFIER'

    # Pass in any empty object
    p[0] = {'name': p[1]}

    debug.printError("No hint provided for variable '%s'" %p[1])
    raise SyntaxError

def p_insertArgs(p):
    'M_insertArgs : empty'

    # Add identifiers to local scope
    for argument in p[-2]:
        # Any callback is stored as a CALLBACK which is a different type
        if ST.existsInCurrentScope(argument['name']):
            debug.printError("Redefinition of argument '%s'" %argument['name'])
            raise SyntaxError
        else:
            if argument['type'] == 'FUNCTION':
                ST.addIdentifier(argument['name'], 'CALLBACK')
            else:
                ST.addIdentifier(argument['name'], argument['type'])

            # store the address into the address descriptor
            # The parameters have to loaded in form memory
            displayValue, offset = ST.getAttribute(argument['name'], 'scopeLevel'), ST.getAttribute(argument['name'], 'offset')
            place = ST.newTemp((displayValue, offset), variable=argument['name'], loadFromMemory=True)
            ST.addAttribute(argument['name'],  ST.getCurrentScope(), place)

            debug.printStatementBlock("Argument '%s' of type '%s'" %(argument['name'], argument['type']))

    # Now we store the number of parameters in the function
    ST.addAttributeToCurrentScope('numParam', len(p[-2]))

########################################
######## RETURN STATEMENT ##############
########################################
def p_returnStatement(p):
    'returnStatement : RETURN expression'

    # Type rules
    p[0] = { 'type' : p[2]['type'] }

    # Get the current returnType from function
    returnType = ST.getAttributeFromCurrentScope('returnType')

    # If the function has not been assigned a return type as of yet
    if returnType == 'UNDEFINED':
        # Assign a returnType to the function
        if p[2]['type'] == 'FUNCTION':
            ST.addAttributeToCurrentScope('returnType', 'CALLBACK')
            debug.printStatement("Return statement of type 'CALLBACK'")
        else:
            ST.addAttributeToCurrentScope('returnType', p[2]['type'])
            debug.printStatement("Return statement of type '%s'" %p[2]['type'])

    elif p[2]['type'] != returnType:
        p[0]['type'] = 'TYPE_ERROR'
        debug.printError('Return Types dont match')
        raise SyntaxError

    else:
        # In this case, the return types match, so we needn't do anything
        pass

    # Emit code for the return type
    TAC.emit(p[2]['place'], '' ,'', 'RETURN')

########################################
######## FUNCTIONS CALLS ###############
########################################
def p_functionCall(p):
    'functionCall : IDENTIFIER SEP_OPEN_PARENTHESIS actualParameters SEP_CLOSE_PARENTHESIS'

    p[0] = {}

    # If the identifier does not exist then we output error
    if not ST.exists(p[1]):
        p[0]['type'] = 'REFERENCE_ERROR'
        debug.printError("Function '%s' is not defined" %p[1])
        raise SyntaxError
    else:
        identifierType = ST.getAttribute(p[1], 'type')

        # If the function exists in the current scope
        if identifierType in [ 'FUNCTION', 'CALLBACK' ]:
            if not ST.existsInCurrentScope(p[1]):
                # The definition of the function has to be loaded in from memory
                displayValue, offset = ST.getAttribute(p[1], 'scopeLevel'), ST.getAttribute(p[1], 'offset')
                place = ST.newTemp((displayValue, offset),variable=p[1], loadFromMemory=True)
                ST.addAttribute(p[1], ST.getCurrentScope(), place)
            else:
                place = ST.getAttribute(p[1], ST.getCurrentScope())

            # Now we print the param statements
            for param in p[3]:
                TAC.emit(param, '', '', 'PARAM')

            # The name of the function
            debug.printStatementBlock("Function call to '%s'" %p[1])

            # We jump to the function
            TAC.emit('', '', place, 'JUMPLABEL')

            # In case the function call is used in an expression
            # The type of the statment is dependent on the input condition
            if identifierType != 'CALLBACK':
                reference = ST.getAttribute(p[1], 'reference')
                p[0]['type'] = ST.getAttributeFromFunctionList(reference, 'returnType')

                if p[0]['type'] != 'CALLBACK':
                    returnPlace = ST.newTemp()
                    TAC.emit(returnPlace, '', '', 'FUNCTION_RETURN')

                    p[0]['place'] = returnPlace
            else:
                p[0]['type'] = 'CALLBACK'
        else:
            p[0]['type'] = 'REFERENCE_ERROR'
            debug.printError('Not a function "%s"' %p[1])
            raise SyntaxError

def p_parameters(p):
    'actualParameters : expression SEP_COMMA actualParameters'

    p[0] = [p[1]['place']] + p[3]

def p_parameters_base(p):
    'actualParameters : expression'

    p[0] = [p[1]['place']]

def p_parameters_empty(p):
    'actualParameters : empty'

    p[0] = []

########################################
######## BREAK STATEMENT ###############
########################################
def p_breakStatement(p):
    'breakStatement : BREAK'

    debug.printStatement('Break')

    # Type rules
    p[0] = {}

    # Emit code
    p[0]['loopEndList'] = [TAC.getNextQuad()]
    TAC.emit('', '', -1, 'GOTO')

########################################
######## CONTINUE STATEMENT ############
########################################
def p_continueStatement(p):
    'continueStatement : CONTINUE'

    debug.printStatement('Continue')

    # Type rules
    p[0] = {}

    # Emit code
    p[0]['loopBeginList'] = [TAC.getNextQuad()]
    TAC.emit('', '', -1, 'GOTO')

########################################
############# IF THEN ##################
########################################
def p_ifThen(p):
    'ifThen : IF SEP_OPEN_PARENTHESIS expression SEP_CLOSE_PARENTHESIS M_ifBranch block'

    # Type rules
    if p[3]['type'] != 'BOOLEAN':
        debug.printError('If condition must be a boolean')
        raise SyntaxError

    p[0] = {}

    # For break statement and next waiting functions
    p[0]['nextList'] = TAC.merge(p[5].get('falseList', []), p[6].get('nextList', []))
    p[0]['loopEndList'] = p[6].get('loopEndList', [])
    p[0]['loopBeginList'] = p[6].get('loopBeginList',[])

########################################
############# IF THEN ELSE #############
########################################
def p_ifThenElse(p):
    'ifThenElse : IF SEP_OPEN_PARENTHESIS expression SEP_CLOSE_PARENTHESIS M_ifBranch block ELSE M_elseBranch block'

    # Type rules
    if p[3]['type'] != 'BOOLEAN':
        debug.printError('If condition must be a boolean')
        raise SyntaxError

    p[0] = {}

    # backPatch the if branch
    TAC.backPatch(p[5]['falseList'], p[8]['quad'])
    p[0]['nextList'] = p[8]['nextList']

    # For break statement
    p[0]['loopEndList'] = TAC.merge(p[9].get('loopEndList', []), p[6].get('loopEndList', []))
    p[0]['loopBeginList'] = TAC.merge(p[9].get('loopBeginList', []), p[6].get('loopBeginList', []))

def p_m_ifBranch(p):
    'M_ifBranch : empty'

    # Print to the console
    debug.printStatementBlock("If Branch")

    p[0] = {}
    p[0]['falseList'] = [TAC.getNextQuad()]
    TAC.emit(p[-2]['place'], '', -1, 'COND_GOTO_Z')

def p_m_elseBranch(p):
    'M_elseBranch : empty'

    # Print to the console
    debug.printStatementBlock("Else Branch")

    p[0] = {}
    p[0]['nextList'] = [TAC.getNextQuad()]
    TAC.emit('', '', -1, 'GOTO')

    p[0]['quad'] = TAC.getNextQuad()

########################################
########## WHILE STATEMENT #############
########################################
def p_while(p):
    'whileStatement : WHILE M_quad SEP_OPEN_PARENTHESIS expression SEP_CLOSE_PARENTHESIS M_whileBranch block'

    # Emit code
    p[0] = {}
    p[0]['nextList'] = []

    # Backpatch
    if p[4]['type'] == 'BOOLEAN':
        # Backpatch continue statements and break statements
        TAC.backPatch(p[7]['loopBeginList'], p[2]['quad'])
        p[0]['nextList'] = TAC.merge(p[7].get('loopEndList', []), p[7].get('nextList', []))
        p[0]['nextList'] = TAC.merge(p[6].get('falseList', []), p[0].get('nextList', []))

        # Loop around
        TAC.emit('', '', p[2]['quad'], 'GOTO')
    else:
        debug.printError('The condition of while should be a boolean')
        raise SyntaxError

    p[0]['type'] = 'VOID'

def p_m_whileBranch(p):
    'M_whileBranch : empty'

    p[0] = {}
    p[0]['falseList'] = [TAC.getNextQuad()]
    TAC.emit(p[-2]['place'], '', -1, 'COND_GOTO_Z')

    # Print to the console
    debug.printStatementBlock("While Statement")

########################################
############## PRINT ###################
########################################
def p_printStatement(p):
    'printStatement : CONSOLE OP_DOT LOG SEP_OPEN_PARENTHESIS printList SEP_CLOSE_PARENTHESIS'

    p[0] = {}

    for printIterator in p[5]:
        # Check if the given expression is printable or not
        expType = printIterator.get('type')
        if expType in ['STRING', 'NUMBER', 'BOOLEAN', 'UNDEFINED']:
            TAC.emit(printIterator['place'], '', printIterator['type'], 'PRINT')
            debug.printStatement("Print Statement of type %s" %printIterator['type'])
        else:
            debug.printError('Given expression is not a printable type')
            raise SyntaxError

    # We print a new line
    # TAC.emit('', '', 'NEW_LINE', 'PRINT')

def p_printList(p):
    'printList : expression SEP_COMMA printList'

    p[0] = [ { 'place': p[1]['place'], 'type' : p[1]['type'] } ] + p[3]

def p_printList_base(p):
    'printList : expression'''

    p[0] = [ { 'place': p[1]['place'], 'type' : p[1]['type'] } ]

def p_printList_empty(p):
    'printList : empty'''

    p[0] = []


########################################
############## EXPRESSIONS #############
########################################
# Precedence of operators
precedence = (
        ('left', 'OP_OR'),
        ('left', 'OP_AND'),
        ('left', 'OP_EQUALS', 'OP_NOT_EQUALS'),
        ('left', 'OP_LESS_THEN', 'OP_GREATER_THEN', 'OP_LESS_THEN_E', 'OP_GREATER_THEN_E'),
        ('left', 'OP_PLUS', 'OP_MINUS'),
        ('left', 'OP_MULTIPLICATION', 'OP_DIVISION', 'OP_MODULUS'),
        ('right', 'UMINUS', 'OP_TYPEOF', 'OP_NOT'),
        )

######## UNARY EXPRESSIONS ############

def p_expression_unary(p):
    '''expression : OP_MINUS expression %prec UMINUS
                  | OP_TYPEOF expression'''

    # Type rules
    expType = 'UNDEFINED'

    # Emit code
    p[0] = {}
    p[0]['place'] = ST.newTemp()

    # Conditional branch to figure out what code to emit and check types
    if p[1] == '-':
        if p[2]['type'] == 'NUMBER':
            expType = 'NUMBER'
            TAC.emit(p[0]['place'], p[2]['place'] , '' , 'uni-')
        else:
            expType = 'TYPE_ERROR'
            debug.printError('Type Mismatch in expression')
            raise SyntaxError
    else:
        expType = 'STRING'
        TAC.emit(p[0]['place'], p[2]['type'] , '' , '=')

    # Return type of the statment
    p[0]['type'] = expType

######## BINARY EXPRESSIONS ############

def p_expression_binop(p):
    '''expression : expression OP_PLUS expression
                  | expression OP_MINUS expression
                  | expression OP_MULTIPLICATION expression
                  | expression OP_DIVISION expression
                  | expression OP_MODULUS expression'''

    # Type rules
    expType = 'UNDEFINED'

    # To store information
    p[0] = {}
    p[0]['place'] = ST.newTemp()

    # To emit codes
    if p[1]['type'] == 'NUMBER' and p[3]['type'] == 'NUMBER':
        expType = 'NUMBER'
        TAC.emit(p[0]['place'], p[1]['place'], p[3]['place'], p[2])
    else:
        expType = 'TYPE_ERROR'
        debug.printError('Type Mismatch in Arithematic Expression')
        raise SyntaxError

    p[0]['type'] = expType

######## RELATIONAL EXPRESSION ############

def p_expression_relational(p):
    '''expression : expression OP_GREATER_THEN expression
                  | expression OP_GREATER_THEN_E expression
                  | expression OP_LESS_THEN expression
                  | expression OP_LESS_THEN_E expression
                  | expression OP_EQUALS expression
                  | expression OP_NOT_EQUALS expression'''

    # Type rules
    expType = 'UNDEFINED'

    if p[1]['type'] == p[3]['type'] == 'NUMBER':
        expType = 'BOOLEAN'
    else:
        expType = 'TYPE_ERROR'
        debug.printError('Operands to relational expressions must be numbers')
        raise SyntaxError

    p[0] = { 'type' : expType }
    p[0]['place'] = ST.newTemp()

    # Emit code
    TAC.emit(p[0]['place'], p[1]['place'], p[3]['place'], p[2])

######## LOGICAL EXPRESSION ##############

def p_expression_logical_and(p):
    'expression : expression OP_AND M_quad expression'

    # Type rules
    expType = 'BOOLEAN'

    # Backpatching code
    p[0] = {}
    p[0]['place'] = ST.newTemp()

    if p[1]['type'] == p[4]['type'] == 'BOOLEAN':
        expType = 'BOOLEAN'
        TAC.emit(p[0]['place'], p[1]['place'], p[4]['place'] , p[2])
    else:
        expType = 'TYPE_ERROR'
        debug.printError('Operands to logical expressions must be integers')
        raise SyntaxError

    # Type of the expression
    p[0]['type'] = expType

def p_expression_logical_or(p):
    'expression : expression OP_OR M_quad expression'

    # Type rules
    expType = 'UNDEFINED'

    # Backpatching code
    p[0] = {}
    p[0]['place'] = ST.newTemp()

    if p[1]['type'] == p[4]['type'] == 'BOOLEAN':
        expType = 'BOOLEAN'
        TAC.emit(p[0]['place'], p[1]['place'], p[4]['place'] , p[2])
    else:
        expType = 'TYPE_ERROR'
        debug.printError('Operands to logical expressions must be integers')
        raise SyntaxError

    # Type of the expression
    p[0]['type'] = expType

def p_expression_logical_not(p):
    'expression : OP_NOT expression'

    # Type rules
    expType = 'BOOLEAN'

    # Backpatching code
    p[0] = {}
    p[0]['place'] = ST.newTemp()

    if p[2]['type'] != 'BOOLEAN':
        expType = 'TYPE_ERROR'
        debug.printError('Operands to logical expressions must be integers')
        raise SyntaxError
    else:
        TAC.emit(p[0]['place'], p[2]['place'], '' , p[1])

    # Type of the expression
    p[0]['type'] = expType

######## GROUP EXPRESSION ##############

def p_expression_group(p):
    'expression : SEP_OPEN_PARENTHESIS expression SEP_CLOSE_PARENTHESIS'

    # Type rules
    p[0] = { 'type' : p[2]['type'] }

    # emit code
    p[0]['place'] = p[2]['place']

    # Backpatching code
    if p[2]['type'] == 'BOOLEAN':
        p[0]['trueList'] = p[2].get('trueList', [])
        p[0]['falseList'] = p[2].get('falseList', [])

######## BASE TYPE EXPRESSION ###########

def p_expression_baseType(p):
    'expression : baseType'

    # Type rules
    p[0] = { 'type' : p[1]['type'] }

    p[0]['place'] = ST.newTemp()

    # emit code for backPatch
    if p[1]['type'] in ['FUNCTION', 'STRING']:
        p[0]['reference'] = p[1]['reference']
        TAC.emit(p[0]['place'], p[0]['reference'], '', '=REF')
    else:
        TAC.emit(p[0]['place'], p[1]['value'], '', '=i')

######## IDENTIFIER EXPRESSION ###########

def p_expression_identifier(p):
    'expression : IDENTIFIER'

    # Type rules
    p[0] = {}

    # We have to check if the identifier exists in the current scope or not, and
    # accordingly load it in
    if ST.exists(p[1]):
        p[0]['type'] = ST.getAttribute(p[1], 'type')

        # Here we have to load in the value of the variable
        if not ST.existsInCurrentScope(p[1]):
            # If an identifier is used, we assume that it is present in memory
            displayValue, offset = ST.getAttribute(p[1], 'scopeLevel'), ST.getAttribute(p[1], 'offset')
            p[0]['place'] = ST.newTemp((displayValue, offset), variable=p[1], loadFromMemory=True)
            ST.addAttribute(p[1], ST.getCurrentScope(), p[0]['place'])
        else:
            p[0]['place'] = ST.getAttribute(p[1], ST.getCurrentScope())
    else:
        p[0]['type'] = 'REFERENCE_ERROR'
        debug.printError('Undefined Variable "%s"' %p[1])
        raise SyntaxError

######## FUNCTION CALLS ##################
def p_expression_functionCall(p):
    'expression : functionCall'

    # Return the value of the function
    p[0] = {}
    p[0]['type'] = p[1]['type']

    if p[1]['type'] == 'CALLBACK':
        debug.printError('Callback functions cannot be used as expressions')
        raise SyntaxError
    else:
        p[0]['place'] = p[1]['place']

######## ARRAY EXPRESSION ################
def p_expression_array(p):
    'expression : array'

    p[0] = {}
    print "array"

########################################
########## BASE TYPES ##################
########################################

def p_baseType_number(p):
    'baseType : NUMBER'

    # Type rules
    p[0] = { 'type' : 'NUMBER', 'value' : int(p[1]) }

def p_baseType_boolean(p):
    'baseType : BOOLEAN'

    # Type rules
    if p[1] == 'true':
        value = 1
    else:
        value = 0
    p[0] = { 'type' : 'BOOLEAN' , 'value' : value }

def p_baseType_string(p):
    'baseType : STRING'

    # Type rules
    p[0] = { 'type' : 'STRING' , 'reference': ST.nameString(), 'value' : p[1] }

    # Whenever a string is defined, we have to add it to the function's data region
    ST.addToStringList(p[0]['reference'], p[1])

def p_baseType_undefined(p):
    'baseType : UNDEFINED'

    # Type rules
    p[0] = { 'type' : 'UNDEFINED', 'value' : 0}

######## FUNCTION EXPRESSION ###########

def p_baseType_function(p):
    'baseType : functionStatement'

    # Type rules
    p[0] = { 'type': 'FUNCTION', 'reference': p[1]['reference']}

####### ARRAY EXPRESSIONS ##############

def p_baseType_array(p):
    'array : SEP_OPEN_BRACKET arrayList SEP_CLOSE_BRACKET'

    p[0] = {'type': 'NUMBER'}

def p_arrayList(p):
    'arrayList : expression SEP_COMMA arrayList'

    print p[3]
    if p[3]['type'] == 'UNDEFINED':
        p[0] = {'value': p[1]['place'], 'type' : p[1]['type']}
    elif p[1]['type'] == p[3]['type']:
        p[0] = {'value': [p[1]['place']] + p[3]['value'], 'type' : p[1]['type']}
    else:
        debug.printError('Elements of an array must be of the same type')

def p_arrayList_base(p):
    'arrayList : expression'

    p[0] = {'value': [p[1]['place']], 'type' : p[1]['type']}

def p_arrayList_empty(p):
    'arrayList : empty'

    p[0] = {'value': [], 'type': 'UNDEFINED'}

########################################
################ EMPTY #################
########################################
def p_empty(p):
    'empty :'

    p[0] = {}

########################################
############# ERROR ####################
########################################
def p_error(p):
    debug.printError("Whoa. You are seriously hosed.")

    # Read ahead looking for a closing '}'
    tok = parser.token()
    if not tok:
        while 1:
            if not tok or tok.type in ['SEP_SEMICOLON', 'SEP_OPEN_BRACE', 'SEP_CLOSE_BRACE']:
                break
            tok = parser.token()             # Get the next token
        parser.restart()
        # parser.errok()

######################################################################################################

######## Required Globals ##############
ST = SymbolTable.SymbolTable()
TAC = ThreeAddressCode.ThreeAddressCode(ST)
parser = yacc.yacc()
########################################

def parseProgram(program):
    parser.parse(program, lexer=lexer)
    return ST, TAC, debug

# a function to test the parser
def testYacc(inputFile):
    program = open(inputFile).read()
    parser.parse(program, lexer=lexer)
    # parser.parse(program, lexer=lexer, debug=1)

if __name__ == "__main__":
    from sys import argv
    filename, inputFile = argv

    testYacc(inputFile)