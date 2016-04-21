import sys
import pprint
import copy
import re
operators = ["=", "~", "!", "&", "+", "-", "*", "/", "%", "&", "|", "^", "<<", ">>", "ifgoto", "&", "pointer", "address", "goto"]
non_operators = ['param', 'call', 'ret', 'label', 'print']
rel_operators = ['jl', 'jg', 'je', 'jle', 'jge']
leaders = [1]
lang = operators + non_operators + rel_operators
register_descriptor = {}
all_variables = []
basic_blocks = []
for x in ['eax', 'ebx', 'ecx', 'edx', 'esi', 'edi']:
    temp_obj = {}
    temp_obj['state'] = "empty"
    temp_obj['temp'] = -1
    register_descriptor[x] = temp_obj

label_flag = {}
label_flag['state'] = False
arrays = []
var_descriptor = {}
num_format = re.compile("^[\-]?[1-9][0-9]*\.?[0-9]+$")

def asm_copy(a, b):
    # movles a to b
    print "\tmovl "+str(a)+", "+str(b)

def getreg(var, op, symbol_table):
    # if op=='/':

    # check if var is also in register
    if var_descriptor[var]['location'] == 'register':
        # print 'register already alloted for '+var
        return (True, var_descriptor[var]['reg_value'])


    # find empty register and return that
    for reg in register_descriptor:
        if register_descriptor[reg]['state'] == 'empty':
            register_descriptor[reg]['state'] = 'filled'
            register_descriptor[reg]['temp'] = var
            var_descriptor[var]['location'] = 'register'
            var_descriptor[var]['reg_value'] = reg
            return (False, var_descriptor[var]['reg_value'])


    # heuristic farthest next use
    farthest_next_use = -1
    farthest_next_use_var = ''
    farthest_next_use_reg = 0
    for reg in register_descriptor:
        a = register_descriptor[reg]['temp']
        if a not in symbol_table:
            farthest_next_use_reg = reg
            farthest_next_use_var = a
            break

        if(symbol_table[a]['state'] == 'dead'):
            farthest_next_use_reg = reg
            farthest_next_use_var = a
            break
        if(farthest_next_use < symbol_table[a]['next_use']):
            farthest_next_use = symbol_table[a]['next_use']
            farthest_next_use_var = a
            farthest_next_use_reg = reg
    # print "heuristic"
    asm_copy('%'+farthest_next_use_reg, farthest_next_use_var)
    var_descriptor[var]['location'] = 'register'
    var_descriptor[var]['reg_value'] = farthest_next_use_reg
    register_descriptor[farthest_next_use_reg]['state'] = 'filled'
    register_descriptor[farthest_next_use_reg]['temp'] = var
    return (False, var_descriptor[var]['reg_value'])
            

def print_assembly(basic_block, var_in_each_line, list_symbol_tables, index):
    
    op = basic_block[index][1]
    # print "op = "+op
    not_good_ops = ['/', '%', 'print', '>>', '<<', 'pointer', 'address']
    if op not in not_good_ops:
        var_count = 0   
        for temp_var in var_in_each_line[index]:
            # print (temp_var, var_descriptor[temp_var])
            var_count = var_count + 1
            var_index = var_in_each_line[index].index(temp_var)
            (already, temp_reg) = getreg(temp_var, op, list_symbol_tables[index])
            if len(var_in_each_line[index])>1:
                if not already:
                    print "\tmovl "+temp_var+", %"+temp_reg
            var_in_each_line[index][var_index] = '%'+temp_reg
            # print (temp_var, var_descriptor[temp_var])
            # print (temp_reg, register_descriptor[temp_reg])
        if op=='=':
            t = basic_block[index][len(basic_block[index])-1]
            try:
                userInput = int(t)
            except:
                isnumber = False
            else:
                isnumber = True
            if isnumber:
                t = '$'+t
            else:
                t = var_in_each_line[index][len(basic_block[index])-1]
            print "\tmovl "+t+", "+var_in_each_line[index][0]
            # if len(var_in_each_line[index])==1:
            #   print "\tmovl %"+var_in_each_line[index][0]+", $"+basic_block[index][len(basic_block[index])-1]
            # elif len(var_in_each_line[index])==2:
            #   print "\tmovl %"+var_in_each_line[index][0]+", %"+basic_block[index][len(basic_block[index])-1] 
        elif op=='+':
            print "\taddl "+var_in_each_line[index][1]+", "+var_in_each_line[index][0]
        elif op=='*':
            print "\timul "+var_in_each_line[index][1]+", "+var_in_each_line[index][0]
        elif op=='-':
            print "\tsubl "+var_in_each_line[index][1]+", "+var_in_each_line[index][0]
        elif op=='<<':
            print "\tshl "+var_in_each_line[index][0]+", "+var_in_each_line[index][1]
        elif op=='>>':
            print "\tshr "+var_in_each_line[index][0]+", "+var_in_each_line[index][1]
        elif op=='ifgoto':
            # print "\tifgoto"
            # print var_in_each_line[index]
            print "\tcmp "+var_in_each_line[index][1]+", "+var_in_each_line[index][0]
            block_index = leaders.index(int(basic_block[index][5]))
            print '\t'+basic_block[index][2]+" L"+str(block_index+1) 
        elif op=='goto':
            block_index = leaders.index(int(basic_block[index][2]))
            print "\tjmp L"+str(block_index+1)
        elif op=='call':
            func = basic_block[index][2]
            for reg in register_descriptor:
                # print (reg, register_descriptor[reg])
                if register_descriptor[reg]['state']!='empty':
                    temp_var = register_descriptor[reg]['temp']
                    # print (temp_var, var_descriptor[temp_var])
                    print '\tmovl %'+reg+', '+temp_var
                    register_descriptor[reg]['state']='empty'
                    var_descriptor[temp_var]['location'] = 'memory'
            print "\tcall "+func
            # for block in basic_blocks:
            #   print func
            #   if func in block and block[1]=='label':
            #       block_index = basic_blocks.index(block)
            #       print "\tjmp "+func
            #       break
        elif op=='label':
            print basic_block[index][2]+":"
            label_flag['state'] = True
        elif op=='ret':
            for reg in register_descriptor:
                if register_descriptor[reg]['state']!='empty':
                    temp_var = register_descriptor[reg]['temp']
                    var_descriptor[temp_var]['location'] = 'memory'
                    register_descriptor[reg]['state'] = 'empty'
                    print '\tmovl %'+reg+', '+temp_var
            if label_flag['state']==True:
                print '\tret'
            else:
                print '\tcall end_label'
        elif op=='|':
            print '\torl '+var_in_each_line[index][1]+', '+var_in_each_line[index][0]
        elif op=='&':
            print '\tandl '+var_in_each_line[index][1]+', '+var_in_each_line[index][0]
        elif op=='^':
            print '\txorl '+var_in_each_line[index][1]+', '+var_in_each_line[index][0]
        elif op=='!':
            print '\tnotl '+var_in_each_line[index][0]
        elif op=='~':
            print '\tnegl '+var_in_each_line[index][0]
        else:
            print ('HEY',basic_block[index])
        return
    
    if op=='/' or op=='%':
        destination = var_in_each_line[index][0]
        source = var_in_each_line[index][1]
        backup_reg = ['eax', 'ebx', 'edx']
        for reg in backup_reg:
            if register_descriptor[reg]['state'] == 'filled':
                temp_var = register_descriptor[reg]['temp']
                print '\tmovl %'+reg+", "+temp_var
                var_descriptor[temp_var]['location'] = 'memory'
        print "\tmovl $0, %edx"
        
        if var_descriptor[destination]['location']=='memory':
            print "\tmovl "+destination+", %eax"
        else:
            temp_reg = var_descriptor[destination]['reg_value']
            print "\tmovl %"+temp_reg+", %eax"  
            register_descriptor[temp_reg]['state'] = 'empty'
        
        if var_descriptor[source]['location']=='memory':
            print "\tmovl "+source+", %ebx"
        else:
            temp_reg = var_descriptor[source]['reg_value']
            print "\tmovl %"+temp_reg+", %ebx"  
            register_descriptor[temp_reg]['state'] = 'empty'
        
        var_descriptor[source]['location'] = 'register'
        var_descriptor[source]['reg_value'] = 'ebx'
        register_descriptor['ebx']['state'] = 'filled'
        register_descriptor['ebx']['temp'] = source

        if op=='/':
            register_descriptor['edx']['state'] = 'empty'
            var_descriptor[destination]['location'] = 'register'
            var_descriptor[destination]['reg_value'] = 'eax'
            register_descriptor['eax']['state'] = 'filled'
            register_descriptor['eax']['temp'] = destination

        else:
            register_descriptor['edx']['state'] = 'filled'
            register_descriptor['edx']['temp'] = destination
            var_descriptor[destination]['location'] = 'register'
            var_descriptor[destination]['reg_value'] = 'edx'
            register_descriptor['eax']['state'] = 'empty'

        print "\tdivl %ebx"
        return

    elif op=='print':
        to_print = var_in_each_line[index][0]
        if var_descriptor[to_print]['location']=='register':
            reg = var_descriptor[to_print]['reg_value']
            print '\tmovl %'+reg+', '+to_print
            var_descriptor[to_print]['location'] = 'memory'
            register_descriptor[reg]['state'] = 'empty'
        for reg in ['eax', 'ebx', 'ecx', 'edx', 'esi']:
            if register_descriptor[reg]['state'] != 'empty':
                temp_var = register_descriptor[reg]['temp']
                var_descriptor[temp_var]['location'] = 'memory'
                print '\tmovl %'+reg+', '+temp_var
                register_descriptor[reg]['state'] = 'empty'
        
        print '\tpushl '+to_print
        print '\tcall printIntNumber'
        print '\tpopl '+to_print

        # print "\tmovl $("+to_print+"), %ecx"
        # print "\tmovl (%ecx), %eax    #number transferred to register eax"
        # print "\tmovl $0, %esi        #counts number of digits"
        # print "\tcall P1"
    elif op=='<<' or op=='>>':
        number = var_in_each_line[index][0]
        to_shift = var_in_each_line[index][1]
        if var_descriptor[number]['location']=='register':
            temp_reg = var_descriptor[number]['reg_value']
            print '\tmovl %'+temp_reg+', '+number
            var_descriptor[number]['location'] = 'memory'
            register_descriptor[temp_reg]['state'] = 'empty'
        if var_descriptor[to_shift]['location']=='register':
            temp_reg = var_descriptor[to_shift]['reg_value']
            print '\tmovl %'+temp_reg+', '+to_shift
            var_descriptor[to_shift]['location'] = 'memory'
            register_descriptor[temp_reg]['state'] = 'empty'
        req_regs = ['eax', 'ecx']
        for reg in req_regs:
            if register_descriptor[reg]['state']!='empty':
                temp_var = register_descriptor[reg]['temp']
                print '\tmovl %'+reg+', '+temp_var
                var_descriptor[temp_var]['location'] = 'memory'
        print '\tmovl '+number+', %eax'
        register_descriptor['eax']['state'] = 'filled'
        register_descriptor['eax']['temp'] = number
        var_descriptor[number]['location'] = 'register'
        var_descriptor[number]['reg_value'] = 'eax'

        print '\tmovl '+to_shift+', %ecx'
        register_descriptor['ecx']['state'] = 'filled'
        register_descriptor['ecx']['temp'] = to_shift
        var_descriptor[to_shift]['location'] = 'register'
        var_descriptor[to_shift]['reg_value'] = 'ecx'
        if op=='<<':
            print '\tshll %cl, %eax'    
        else:
            print '\tshrl %cl, %eax'
    elif op=='pointer':                         # t1 = *t2 or t1 = &t2
        t1 = var_in_each_line[index][0]
        t2 = var_in_each_line[index][1]
        t2_there = False
        for reg in register_descriptor:
            if register_descriptor[reg]['state']!='empty':
                temp_var = register_descriptor[reg]['temp']
                print '\tmovl %'+reg+', '+temp_var
                var_descriptor[temp_var]['location'] = 'memory'
                register_descriptor[reg]['state'] = 'empty'

        (already, temp_reg) = getreg(t1, op, list_symbol_tables[index])
        register_descriptor[temp_reg]['state'] = 'filled'
        register_descriptor[temp_reg]['temp'] = t1
        var_descriptor[t1]['location'] = 'register'
        var_descriptor[t1]['reg_value'] = temp_reg
        
        print '\tmovl ('+t2+'), %'+temp_reg
        print '\tmovl (%'+temp_reg+'), %'+temp_reg
    elif op=='address':
        t1 = var_in_each_line[index][0]     
        (already, temp_reg) = getreg(t1, op, list_symbol_tables[index])
        register_descriptor[temp_reg]['state'] = 'filled'
        register_descriptor[temp_reg]['temp'] = t1
        var_descriptor[t1]['location'] = 'register'
        var_descriptor[t1]['reg_value'] = temp_reg

        t2 = var_in_each_line[index][1]
        print '\tmovl $(' + t2 + '), %'+temp_reg

def return_content(basic_block):
    all_vars_in_this_block = []
    var_in_each_line = []
    non_var = ['label', 'call']
    for code_line in basic_block:
        var_in_this_line = []
        if code_line[1] in non_var:
            var_in_each_line.append(var_in_this_line)
            continue
        for word in code_line:
            if word not in lang:
                try:
                    userInput = int(word)
                except:
                    isnumber = False
                else:
                    isnumber = True
                if not isnumber:
                    var_in_this_line.append(word)
                    if word not in all_vars_in_this_block:
                        all_vars_in_this_block.append(word)

        var_in_each_line.append(var_in_this_line)
    return (all_vars_in_this_block, var_in_each_line)


def process(basic_block):
    ###### preprocess basic block ######
    (all_vars_in_this_block, var_in_each_line) = return_content(basic_block)
    for temp_var in all_vars_in_this_block:
        if temp_var not in var_descriptor:
            var_obj = {}
            var_obj['location'] = 'memory'
            var_obj['reg_value'] = -1
            var_descriptor[temp_var] = var_obj
    # end of preprocess #

    ###### symbol tables #######
    list_symbol_tables = []
    symbol_table = {}
    for temp in all_vars_in_this_block:
        temp_obj = {}
        temp_obj['state'] = 'dead'
        temp_obj['last_use'] = -1
        temp_obj['next_use'] = -1
        symbol_table[temp] = temp_obj
    if len(symbol_table)==0:
        # uncomment it afterwards
        symbol_table = {}
        for line_code in basic_block:
            list_symbol_tables.append(symbol_table)
        for line_code in basic_block:
            line_index = basic_block.index(line_code)
            print_assembly(basic_block, list_symbol_tables, var_in_each_line, line_index)
        # print "\t\n"
        return
    else:
        list_symbol_tables = [symbol_table]
        for line_code in reversed(basic_block):
            symbol_table = copy.deepcopy(symbol_table)
            index = basic_block.index(line_code)
            if len(var_in_each_line[index])==0:
                continue
            destination = var_in_each_line[index][0]
            if destination[0] == '$':
                if symbol_table[destination]['state']!='dead':
                    symbol_table[destination]['state'] = 'dead'
            temp_count = 1
            while temp_count<len(var_in_each_line[index]):
                source = var_in_each_line[index][temp_count]
                if source[0]=='$':
                    if(symbol_table[source]['state']=='dead'):
                        symbol_table[source]['state'] = 'live'
                        symbol_table[source]['last_use'] = index
                        symbol_table[source]['next_use'] = index
                    else:
                        symbol_table[source]['next_use'] = index
                temp_count = temp_count + 1
            list_symbol_tables.insert(0, symbol_table)
    # end of symbol tables #


    for line_code in basic_block:
        index = basic_block.index(line_code)
        print_assembly(basic_block, var_in_each_line, list_symbol_tables, index)
        # pprint.pprint(basic_block[index])

    ###### empty all registers ######
    # for temp_var in var_descriptor:
    #   if var_descriptor[temp_var]['location'] == 'register':
    #       temp_reg = var_descriptor[temp_var]['reg_value']
    #       asm_copy('$'+temp_reg, temp_var)
    #       var_descriptor[temp_var]['location'] = 'memory'
    #       register_descriptor[temp_reg]['state'] = 'empty'
    #       register_descriptor[temp_reg]['temp'] = -1
    # end of empty all registers #
    

if __name__ == '__main__':
    input_file_name = './' + sys.argv[1]
    with open(input_file_name, 'rb') as file:
        input_code = file.readlines()
    
    # forming splitted code
    splitted_code = []
    for input_line in input_code:
        temp = input_line.split(", ")
        temp[len(temp)-1] = temp[len(temp)-1][:-1]
        splitted_code.append(temp)
    # pprint.pprint(splitted_code)
    to_be_removed = []
    for line_code in splitted_code:
        if line_code[1] == 'array_def':
            temp = {}
            temp['array_name'] = line_code[2]
            temp['array_size'] = line_code[3]
            arrays.append(temp)
            to_be_removed.append(line_code)
    for x in to_be_removed:
        splitted_code.remove(x)
    count = 1
    for line_code in splitted_code:
        line_code[0] = str(count)
        count = count + 1
    # finding leaders
    # pprint.pprint(splitted_code)
    temp_count = 1
    for line_code in splitted_code:
        if line_code[0]!='1':
            if line_code[1] == "ifgoto":
                leaders.append(int(line_code[5]))
                if temp_count+1 <= len(splitted_code):
                    leaders.append(temp_count+1)
            elif line_code[1] == "call":
                if temp_count+1 <= len(splitted_code):
                    leaders.append(temp_count+1)
            elif line_code[1] == "goto":
                leaders.append(int(line_code[2]))
            elif line_code[1] == "label":
                leaders.append(temp_count)
        temp_count = temp_count + 1
    # print "\tLeaders:"
    # pprint.pprint(leaders)

    # building basic blocks
    
    temp_basic_block = []
    for line_code in splitted_code:
        index = splitted_code.index(line_code)
        if index == 0:
            temp_basic_block.append(line_code)
        else:
            if index+1 in leaders:
                basic_blocks.append(temp_basic_block)
                temp_basic_block = [line_code]
            else:
                temp_basic_block.append(line_code)
    basic_blocks.append(temp_basic_block)
    # print "\tBasic Blocks"
    # pprint.pprint(basic_blocks)
    count = 0
    not_var_words = ['label', 'call']
    for basic_block in basic_blocks:
        for line_code in basic_block:
            for word in line_code:
                if word not in lang and (line_code[1] not in not_var_words) and word not in all_variables:
                    try:
                        userInput = int(word)
                    except:
                        isnumber = False
                    else:
                        isnumber = True
                    if not isnumber:
                        all_variables.append(word)
    print '.section .text'
    print '\t.global _start'

    # pprint.pprint(all_variables)
    for basic_block in basic_blocks:
        if count==0:
            print '_start:'
        elif basic_block[0][1]!='label':
            print "L"+str(count+1)+":"
        process(basic_block)
        count = count + 1
        print ""
#   print 'P1:'
#   a = '\
#   movl $10, %ecx       #divisor\n\
#   movl $0, %edx        \n\
#   idivl %ecx           #dividing the number by 10\n\
#   addl $48, %edx       #converts to ascii\n\
#   pushl %edx           #digit oushed to stack\n\
#   addl $1, %esi        #count increased\n\
#   cmpl $0, %eax        #checking if all digits accounted for\n\
#   je P2                #loop terminates to print the digits\n\
#   jmp P1 \n\
# P2:                      #second loop for printing the digits\n\
#   movl $4, %eax\n\
#   movl $1, %ebx\n\
#   movl %esp, %ecx\n\
#   addl $4, %esp        #now esp points to the next integer\n\
#   movl $1, %edx\n\
#   int $0x80            #prints current integer\n\
#   subl $1, %esi        #reduces count by one\n\
#   cmpl $0, %esi        #checks whether count is 0\n\
#   je end_print\n\
#   jmp P2               #if not zero then continues the loop\n\
# end_print:\n\
#   ret\n\
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
    ret  \n\
    EndPrintNum:\n'
    print a
    print '.section .data'
    for word in all_variables:
        print word+":"
        print "\t.long 0"
    for array in arrays:
        print array['array_name']+":"
        print "\t.space "+array['array_size']
    print 'type:'
    print '\t.ascii "HELLO %d HELLO\\n\\0"'
