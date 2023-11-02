#!/bin/bash
# Use NGINX binary
binary_path=" /home/aditi/CodeSurgeon/test-nginx-uwsgi/nginx-release-1.25.2/objs/nginx"

export NGINX_PREFIX='nginx_data_files_dir'
# mkdir -p "$NGINX_PREFIX/cache"
# mkdir "$NGINX_PREFIX/logs"


sudo $binary_path -p $NGINX_PREFIX -c /home/aditi/CodeSurgeon/test-nginx-uwsgi/nginx_data_files_dir/nginx-cache.conf

sudo  /home/aditi/CodeSurgeon/test-nginx-uwsgi/nginx-release-1.25.2/objs/nginx -p nginx_data_files_dir -c /home/aditi/CodeSurgeon/test-nginx-uwsgi/nginx_data_files_dir/nginx-cache.conf

uwsgi --socket 127.0.0.1:9000 --wsgi-file server.py



# Perform perf record
# sudo perf record -e intel_pt//u -- ./my_cpp_executable
sudo perf record -e intel_pt//u -- $binary_path -p $NGINX_PREFIX -c /home/aditi/CodeSurgeon/test-nginx-uwsgi/nginx_data_files_dir/nginx-cache.conf


mmap_addr=$(sudo perf script --show-mmap-events | grep MMAP | grep  /home/aditi/CodeSurgeon/test-nginx-uwsgi/nginx-release-1.25.2/objs/nginx)
echo "mmap_addr: $mmap_addr"

base_addr=$(echo $mmap_addr | awk -F'[' '{print $3}' | awk -F'(' '{print $1}')
echo "base_addr: $base_addr"

base_addr_pre="${base_addr:2:8}"
echo "base_addr_pre: $base_addr_pre"


size=$(echo $mmap_addr | awk -F'[' '{print $3}' | awk -F'(' '{print $2}' | awk -F')' '{print $1}')
# 0x5570a7114000
# 70a71140
# 5570a711
echo "base_addr_pre: $base_addr_pre"
echo "size: $size"

sudo perf script --insn-trace | grep $base_addr_pre > temp11.txt
lineStart=$(grep -n main+0x temp11.txt | cut -d: -f1 | head -1)
lineEnd=$(grep -n main+0x temp11.txt | cut -d: -f1 | tail -2 | head -1)

echo "lineStart: $lineStart"
echo "lineEnd: $lineEnd"

awk -v f=$lineStart -v l=$lineEnd 'NR>=f && NR<=l' temp11.txt | awk '{print "0x"$5}' > temp22.txt

prev_result=""
while read -r line; do

	addr=$((line - base_addr))
	addr=$(printf "%x" $addr)
	addr="1$addr"
	cur_result=$(addr2line -e  /home/aditi/CodeSurgeon/test-nginx-uwsgi/nginx-release-1.25.2/objs/nginx $addr)

	if [[ "$cur_result" != "$prev_result" ]]
	then
		echo "$cur_result"
	fi

	prev_result=$cur_result

done < temp2.txt




