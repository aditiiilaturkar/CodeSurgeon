import subprocess
import re

def get_line_numbers(filename, pattern):
    command = f"grep -n {pattern} {filename} | cut -d: -f1"
    output = subprocess.check_output(command, shell=True, universal_newlines=True)
    lines = output.strip().splitlines()
    return lines

def convert_address_to_line(base_addr, address):
    bash_command = f'echo $(( {address} - {base_addr} ))'
    process = subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE)
    output, _ = process.communicate()
    addr = output.decode('utf-8').strip()
    addr = hex(int(addr))
    addr = "1" +  addr[2:]  
    command = f'addr2line -e my_cpp_executable {addr}'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    cur_result = output.decode('utf-8').strip()
    return cur_result
 

def get_insn_trace_analysis():
    # perf_record_command = "sudo perf record -e intel_pt//u -- ./my_cpp_executable"
    # process = subprocess.Popen(perf_record_command, shell=True)
    # process.communicate()

    mmap_addr_command = "sudo perf script --show-mmap-events | grep MMAP | grep my_cpp_executable"
    output = subprocess.check_output(mmap_addr_command, shell=True, universal_newlines=True)
    lines = output.splitlines()
    if lines:
        mmap_addr = lines[0]
    else:
        mmap_addr = None

    print(f"mmap_addr: {mmap_addr}")

    size = re.search(r'\((.*?)\)', mmap_addr).group(1)
    print(f"size: {size}")

    base_addr = mmap_addr.split('[')[2]
    base_addr = base_addr.split('(')[0]
    print(f"base_addr: {base_addr}")

    base_addr_pre = base_addr[2:10]
    print(f"base_addr_pre: {base_addr_pre}")

    insn_trace_command = f"sudo perf script --insn-trace | grep {base_addr_pre} > temp1.txt"
    process = subprocess.Popen(insn_trace_command, shell=True)
    process.communicate()

    filename = "temp1.txt"
    pattern = "main+0x"
    line_numbers = get_line_numbers(filename, pattern)
    if len(line_numbers) >= 2:
        lineStart = line_numbers[0]
        lineEnd = line_numbers[-2]

        print(f"lineStart: {lineStart}")
        print(f"lineEnd: {lineEnd}")
    else:
        print("Pattern not found in the file.")
    
    process_lines_command = f"awk -v f={lineStart} -v l={lineEnd} 'NR>=f && NR<=l' temp1.txt | awk '{{print \"0x\"$5}}' > temp2.txt"
    subprocess.Popen(process_lines_command, shell=True)

    prev_result = ""
    with open("temp2.txt", "r") as file:
        for line in file:
            address = line.strip()
            cur_result = convert_address_to_line(base_addr, address)
            if cur_result != prev_result:
                print(cur_result)

            prev_result = cur_result



if __name__ == "__main__":
    subprocess.run(["g++", "-O0", "-g", "main.cpp", "-o", "my_cpp_executable"])
    get_insn_trace_analysis()