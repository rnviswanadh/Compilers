.section .text

	.global _start

_start:
	# pushl temp
	# call printIntNumber
	# popl temp	
	movl $(arr), %eax
	addl $4, %eax
	movl $4, (%eax)
	movl (%eax), %eax
	pushl %eax
	call printIntNumber
	popl %eax

end_label:
	movl $1, %eax
	movl $0, %ebx
	int $0x80

printIntNumber:
	movl 4(%esp), %ecx
	cmpl $0, %ecx
	jge positive_part
	notl %ecx
	inc %ecx
	movl %ecx, %edi
	movl $45, %eax
	pushl   %eax
	movl $4, %eax
	movl $1, %ebx
	movl %esp, %ecx
	movl $1, %edx
	int $0x80
	popl %eax
	movl %edi, %ecx
positive_part:
	movl %ecx, %eax
	movl %esp, %esi
iter_labl:
	cdq
	movl $10, %ebx
	idivl %ebx
	pushl %edx
	cmpl $0, %eax
	jne iter_labl
	jmp print_num
	
print_num:
	popl %edx
	addl $48, %edx
	pushl %edx
	movl $4, %eax
	movl $1, %ebx
	movl %esp, %ecx
	movl $1, %edx
	int $0x80
	popl %edx
	cmp %esp, %esi
	jne print_num
	ret  
EndPrintNum:


.section .data
temp:
	.long 0

arr:
	.space 40
