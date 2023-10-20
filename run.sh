#!/bin/bash

# g++ -O0 -g main.cpp -o my_cpp_executable

# sudo perf record -e intel_pt//u -- ./my_cpp_executable

mmap_addr=$(sudo perf script --show-mmap-events | grep MMAP | grep my_cpp_executable)
echo "mmap_addr: $mmap_addr"

base_addr=$(echo $mmap_addr | awk -F'[' '{print $3}' | awk -F'(' '{print $1}')
echo "base_addr: $base_addr"


base_addr_pre="${base_addr:2:8}"
echo "base_addr_pre: $base_addr_pre"


size=$(echo $mmap_addr | awk -F'[' '{print $3}' | awk -F'(' '{print $2}' | awk -F')' '{print $1}')

echo "base_addr_pre: $base_addr_pre"
echo "size: $size"

sudo perf script --insn-trace | grep $base_addr_pre > temp1.txt

lineStart=$(grep -n main+0x temp1.txt | cut -d: -f1 | head -1)
lineEnd=$(grep -n main+0x temp1.txt | cut -d: -f1 | tail -2 | head -1)

echo "lineStart: $lineStart"
echo "lineEnd: $lineEnd"

awk -v f=$lineStart -v l=$lineEnd 'NR>=f && NR<=l' temp1.txt | awk '{print "0x"$5}' > temp2.txt

prev_result=""
while read -r line; do

	addr=$((line - base_addr))
	addr=$(printf "%x" $addr)
	addr="1$addr"
	cur_result=$(addr2line -e my_cpp_executable $addr)

	if [[ "$cur_result" != "$prev_result" ]]
	then
		echo "$cur_result"
	fi

	prev_result=$cur_result

done < temp2.txt

cat temp3.txt 

rm temp1.txt
rm temp2.txt