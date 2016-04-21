.section .text

	.global _start

_start:
	movl Temporarie0, %edi
	movl $10, %edi
	movl Temporarie1, %eax
	movl %edi, %eax
	movl Temporarie2, %edx
	movl $5, %edx
	addl %edx, %eax
	movl %eax, Temporarie1
	movl %edx, Temporarie2
	movl %edi, Temporarie0
	pushl Temporarie1
	call printIntNumber
	popl Temporarie1
	movl Temporarie3, %edi
	movl $5, %edi
	movl Temporarie5, %eax
	movl Temporarie1, %edx
	movl %edx, %eax
	addl %edi, %eax
	movl %eax, %edx
	movl %edx, Temporarie1
	movl %eax, Temporarie5
	movl %edi, Temporarie3
	pushl Temporarie1
	call printIntNumber
	popl Temporarie1
	movl Temporarie6, %edi
	movl $1, %edi
	movl Temporarie1, %eax
	addl %edi, %eax
	movl %eax, Temporarie1
	movl %edi, Temporarie6
	pushl Temporarie1
	call printIntNumber
	popl Temporarie1
	movl Temporarie7, %edi
	movl $12, %edi
	movl Temporarie9, %eax
	movl Temporarie1, %edx
	movl %edx, %eax
	subl %edi, %eax
	movl %eax, %edx
	movl %edx, Temporarie1
	movl %eax, Temporarie9
	movl %edi, Temporarie7
	pushl Temporarie1
	call printIntNumber
	popl Temporarie1
	movl Temporarie10, %edi
	movl $2, %edi
	movl Temporarie1, %eax
	subl %edi, %eax
	movl %eax, Temporarie1
	movl %edi, Temporarie10
	pushl Temporarie1
	call printIntNumber
	popl Temporarie1
	movl Temporarie11, %edi
	movl $3, %edi
	movl Temporarie13, %eax
	movl Temporarie1, %edx
	movl %edx, %eax
	imul %edi, %eax
	movl %eax, %edx
	movl %edx, Temporarie1
	movl %eax, Temporarie13
	movl %edi, Temporarie11
	pushl Temporarie1
	call printIntNumber
	popl Temporarie1
	movl Temporarie14, %edi
	movl $2, %edi
	movl Temporarie16, %eax
	movl Temporarie1, %edx
	movl %edx, %eax
	movl %eax, Temporarie16
	movl %edx, Temporarie1
	movl %edi, Temporarie14
	movl $0, %edx
	movl Temporarie16, %eax
	movl Temporarie14, %ebx
	divl %ebx
	movl Temporarie1, %edi
	movl %eax, %edi
	movl %edi, Temporarie1
	movl %eax, Temporarie16
	movl %ebx, Temporarie14
	pushl Temporarie1
	call printIntNumber
	popl Temporarie1
	movl Temporarie17, %edi
	movl $2, %edi
	movl Temporarie19, %eax
	movl Temporarie1, %edx
	movl %edx, %eax
	movl %eax, Temporarie19
	movl %edx, Temporarie1
	movl %edi, Temporarie17
	movl $0, %edx
	movl Temporarie19, %eax
	movl Temporarie17, %ebx
	divl %ebx
	movl Temporarie1, %edi
	movl %edx, %edi
	movl %edi, Temporarie1
	movl %ebx, Temporarie17
	movl %edx, Temporarie19
	pushl Temporarie1
	call printIntNumber
	popl Temporarie1
	movl Temporarie20, %edi
	movl $5, %edi
	movl Temporarie21, %eax
	movl %edi, %eax
	movl Temporarie22, %edx
	movl $6, %edx
	movl Temporarie23, %ebx
	movl %edx, %ebx
	movl Temporarie25, %esi
	movl %eax, %esi
	addl %ebx, %esi
	movl Temporarie26, %ecx
	movl %esi, %ecx
	movl %eax, Temporarie21
	movl %ebx, Temporarie23
	movl %ecx, Temporarie26
	movl %edx, Temporarie22
	movl %esi, Temporarie25
	movl %edi, Temporarie20
	pushl Temporarie21
	call printIntNumber
	popl Temporarie21
	pushl Temporarie23
	call printIntNumber
	popl Temporarie23
	pushl Temporarie26
	call printIntNumber
	popl Temporarie26
	movl Temporarie28, %edi
	movl Temporarie21, %eax
	movl %eax, %edi
	movl Temporarie23, %edx
	addl %edx, %edi
	movl Temporarie30, %ebx
	movl %edi, %ebx
	movl Temporarie26, %esi
	addl %esi, %ebx
	movl %ebx, Temporarie30
	movl %eax, Temporarie21
	movl %edx, Temporarie23
	movl %esi, Temporarie26
	movl %edi, Temporarie28
	pushl Temporarie30
	call printIntNumber
	popl Temporarie30
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
	movl $4, %eax
	movl $1, %ebx
	movl $new, %ecx
	movl $1, %edx
	int $0x80
	ret  
EndPrintNum:

.section .data
Temporarie0:
	.long 0
Temporarie1:
	.long 0
Temporarie2:
	.long 0
Temporarie3:
	.long 0
Temporarie5:
	.long 0
Temporarie6:
	.long 0
Temporarie7:
	.long 0
Temporarie9:
	.long 0
Temporarie10:
	.long 0
Temporarie11:
	.long 0
Temporarie13:
	.long 0
Temporarie14:
	.long 0
Temporarie16:
	.long 0
Temporarie17:
	.long 0
Temporarie19:
	.long 0
Temporarie20:
	.long 0
Temporarie21:
	.long 0
Temporarie22:
	.long 0
Temporarie23:
	.long 0
Temporarie25:
	.long 0
Temporarie26:
	.long 0
Temporarie28:
	.long 0
Temporarie30:
	.long 0
new:
	.ascii "
"
