import re
import subprocess
from collections import defaultdict

binary_path = "/home/aditi/CodeSurgeon/test-nginx-uwsgi/nginx-release-1.25.2/objs/nginx"
export_command = "export NGINX_PREFIX='nginx_data_files_dir'"
perf_record_command = f"sudo perf record -e intel_pt//u -- {binary_path} -p $NGINX_PREFIX -c /home/aditi/CodeSurgeon/test-nginx-uwsgi/nginx_data_files_dir/nginx-cache.conf"
perf_script_command = "sudo perf script --show-mmap-events | grep MMAP"


# Execute the export command
subprocess.run(export_command, shell=True)

subprocess.run(perf_record_command, shell=True)

# Execute perf script command
output = subprocess.check_output(perf_script_command, shell=True, text=True)

# Define the regular expression pattern
pattern = r'\[0x([0-9a-fA-F]+)\((0x[0-9a-fA-F]+)\) @ (0x[0-9a-fA-F]+) (\d+:\d+) (\d+) (\d+)\]:\s(.*)$'

# Use regular expression to find matches in the output
matches = re.finditer(pattern, output, re.MULTILINE)

# Define a list to store dictionaries
obj_list = []


for match in matches:
    start_address = match.group(1)
    start_address = start_address.lstrip("0") 
    end_address = hex(int(start_address, 16) + int(match.group(2), 16))[2:] 
    file_offset = match.group(3)[2:]  
    obj_path = match.group(7).split(" ")[1]  # Extract only the file path
    base_addr_pre = start_address[:8]  # Extract base address prefix

    if obj_path == binary_path:
        main_base_addr_pre = base_addr_pre
    # Create a dictionary and append it to obj_list
    obj = {
        "start_address": start_address,
        "end_address": end_address,
        "file_offset": file_offset,
        "obj_path": obj_path,
        "base_addr_pre": base_addr_pre  
    }
    obj_list.append(obj)


# Print the list of dictionaries
for obj in obj_list:
    print(f"Start Address: {obj['start_address']}")
    print(f"End Address: {obj['end_address']}")
    print(f"File Offset: {obj['file_offset']}")
    print(f"Object Path: {obj['obj_path']}")
    print(f"base_addr_pre : {obj['base_addr_pre']}\n")



print(main_base_addr_pre)
insn_trace_command = f"sudo perf script --insn-trace | grep {main_base_addr_pre}"
with open("temp1.txt", "w") as temp_file:
    subprocess.run(insn_trace_command, shell=True, text=True, stdout=temp_file)


lineStart = int(subprocess.check_output("grep -n main+0x temp1.txt | cut -d: -f1 | head -1", shell=True, text=True))
lineEnd = int(subprocess.check_output("grep -n main+0x temp1.txt | cut -d: -f1 | tail -2 | head -1", shell=True, text=True))

print(lineStart)
print(lineEnd)
# Extract relevant lines and addresses
with open('temp1.txt', 'r') as temp1_file:
    lines = temp1_file.readlines()[lineStart-1:lineEnd]
    addresses = [line.split()[4] for line in lines]

# Write addresses to temp2.txt
with open('temp2.txt', 'w') as temp2_file:
    temp2_file.write('\n'.join(addresses))

unique_line_numbers = set()

with open('temp2.txt', 'r') as file:
    addresses = [line.strip() for line in file]

# # Iterate over each address
for addr in addresses:
    addr = addr.lstrip("0x") 
    # print("\n addr --- ", addr)
    # Find the corresponding memory mapping
    
    for obj in obj_list:
        start_addr = obj["start_address"]
        end_addr = obj["end_address"]
        file_offset = obj["file_offset"]
        if start_addr <= addr <= end_addr:
            # print("\n working with ", start_addr, end_addr)
            relative_addr = hex(int(addr, 16) - int(start_addr, 16) + int(file_offset, 16))
           
            binary_path = obj["obj_path"]
            
            command = f'addr2line -e {binary_path} {relative_addr}'
            output = subprocess.check_output(command, shell=True, text=True)
            
            line_number = output.strip()
            if line_number not in unique_line_numbers:
                # print(f'Address: {addr}, Line Number: {line_number}')
                print(f'Line Number: {line_number}')
                unique_line_numbers.add(line_number)
            break
            



