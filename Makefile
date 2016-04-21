all:
	python Parser.py raw.js > codegen
	python preprocess.py codegen > codegen.txt
	python Codegen.py codegen.txt > codegen.s
	as --32 codegen.s -o codegen.o
	ld -m elf_i386 codegen.o -o key -lc -dynamic-linker /lib/ld-linux.so.2
	./key

test1:
	python Parser.py testCases/test1.js > codegen
	python preprocess.py codegen > codegen.txt
	python Codegen.py codegen.txt > codegen.s
	as --32 codegen.s -o codegen.o
	ld -m elf_i386 codegen.o -o key -lc -dynamic-linker /lib/ld-linux.so.2
	./key

test2:
	python Parser.py testCases/test2.js > codegen
	python preprocess.py codegen > codegen.txt
	python Codegen.py codegen.txt > codegen.s
	as --32 codegen.s -o codegen.o
	ld -m elf_i386 codegen.o -o key -lc -dynamic-linker /lib/ld-linux.so.2
	./key

test3:
	python Parser.py testCases/test3.js > codegen
	python preprocess.py codegen > codegen.txt
	python Codegen.py codegen.txt > codegen.s
	as --32 codegen.s -o codegen.o
	ld -m elf_i386 codegen.o -o key -lc -dynamic-linker /lib/ld-linux.so.2
	./key

test4:
	python Parser.py testCases/test4.js > codegen
	python preprocess.py codegen > codegen.txt
	python Codegen.py codegen.txt > codegen.s
	as --32 codegen.s -o codegen.o
	ld -m elf_i386 codegen.o -o key -lc -dynamic-linker /lib/ld-linux.so.2
	./key

test5:
	python Parser.py testCases/test5.js > codegen
	python preprocess.py codegen > codegen.txt
	python Codegen.py codegen.txt > codegen.s
	as --32 codegen.s -o codegen.o
	ld -m elf_i386 codegen.o -o key -lc -dynamic-linker /lib/ld-linux.so.2
	./key

test6:
	python Parser.py testCases/test6.js > codegen
	python preprocess.py codegen > codegen.txt
	python Codegen.py codegen.txt > codegen.s
	as --32 codegen.s -o codegen.o
	ld -m elf_i386 codegen.o -o key -lc -dynamic-linker /lib/ld-linux.so.2
	./key

test7:
	python Parser.py testCases/test7.js > codegen
	python preprocess.py codegen > codegen.txt
	python Codegen.py codegen.txt > codegen.s
	as --32 codegen.s -o codegen.o
	ld -m elf_i386 codegen.o -o key -lc -dynamic-linker /lib/ld-linux.so.2
	./key

test8:
	python Parser.py testCases/test8.js > codegen
	python preprocess.py codegen > codegen.txt
	python Codegen.py codegen.txt > codegen.s
	as --32 codegen.s -o codegen.o
	ld -m elf_i386 codegen.o -o key -lc -dynamic-linker /lib/ld-linux.so.2
	./key

test9:	
	python Parser.py testCases/test9.js > codegen
	python preprocess.py codegen > codegen.txt
	python Codegen.py codegen.txt > codegen.s
	as --32 codegen.s -o codegen.o
	ld -m elf_i386 codegen.o -o key -lc -dynamic-linker /lib/ld-linux.so.2
	./key

