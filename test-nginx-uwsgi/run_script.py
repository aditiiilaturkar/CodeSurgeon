
import re
import subprocess
from collections import defaultdict

inp = input("Enter 'c' for cache or 'nc' for no-cache: ")
if inp == 'c':
    is_cache = True
elif inp == 'nc':
    is_cache = False
else:
    print("Invalid input! \n")
    exit()

port = 8000 if is_cache else 8001


sleep_in_sec = input("Enter seconds to wait: ")


binary_path = "/home/aditi/CodeSurgeon/test-nginx-uwsgi/nginx-release-1.25.2/objs/nginx"
# nginx_pid_command = f"sudo lsof -i:" + str(port) + " | grep nobody | awk '{print $2}'"
nginx_pid_command = f"sudo lsof -i:" + str(port) + " |awk 'NR==3 {print $2}'"

nginx_pid = subprocess.check_output(nginx_pid_command, shell=True, text=True).strip()
perf_record_command = f"sudo perf record -e intel_pt//u -p {nginx_pid} sleep {sleep_in_sec}"
subprocess.run(perf_record_command, shell=True)

perf_script_command = f"sudo perf script --show-mmap-events | grep MMAP | grep {binary_path}"
output = subprocess.check_output(perf_script_command, shell=True, text=True)

pattern = r'\[0x([0-9a-fA-F]+)\((0x[0-9a-fA-F]+)\) @ (0x[0-9a-fA-F]+) (\d+:\d+) (\d+) (\d+)\]:\s(.*)$'

match = re.search(pattern, output)


start_addr = match.group(1)
start_addr = start_addr.lstrip("0") 
file_offset = match.group(3)[2:]  
 
print(f"Start Address: {start_addr}, File Offset: {file_offset}")


insn_trace_command = "sudo perf script --insn-trace | grep " + binary_path + " | awk '{print \"0x\"$5}'"
insn_trace_command_output = subprocess.check_output(insn_trace_command, shell=True, text=True)

addresses = insn_trace_command_output.split()
unique_line_numbers = set()
rel_addrs = [[]]
for addr in addresses:
    addr = addr.lstrip("0x") 

    relative_addr = hex(int(addr, 16) - int(start_addr, 16) + int(file_offset, 16)) 
    if len(rel_addrs[-1]) < 200:
        rel_addrs[-1].append(relative_addr)
    else:
        rel_addrs.append([relative_addr])


for addr_list in rel_addrs:
    addrs = ' '.join(addr_list)
    command = f'addr2line -e {binary_path} {addrs}'
    output_lines = subprocess.check_output(command, shell=True, text=True)
    
    for output in output_lines.split():
        line = output.strip()
        if line not in unique_line_numbers:
            unique_line_numbers.add(line)
    
with open(f"{'cache' if is_cache else 'no_cache'}.txt", 'w') as f:
    for line in list(unique_line_numbers):
        f.write(line + '\n')
        


