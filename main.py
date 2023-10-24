import subprocess
import re

COMMAND_COMPILE = "g++ -O0 -g main.cpp -o my_cpp_executable"
COMMAND_PERF_RECORD = "sudo perf record -e intel_pt//u -- ./my_cpp_executable C"
COMMAND_MMAP = "sudo perf script --show-mmap-events | grep MMAP | grep my_cpp_executable"
COMMAND_INSN_TRACE = "sudo perf script --insn-trace"
COMMAND_ADDR2LINE = "addr2line -e my_cpp_executable "


def exec_command(command, capture_output=False):
    # print(f"\n=========== Executing [[ {command} ]] ===========")
    if capture_output:
        output = subprocess.check_output(command, shell=True, universal_newlines=True)
        lines = output.splitlines()
        return lines
    else:
        process = subprocess.Popen(command, shell=True)
        process.communicate()


if __name__ == "__main__":
    # ============================ STEP 1 ============================
    exec_command(COMMAND_COMPILE)

    # ============================ STEP 2 ============================
    exec_command(COMMAND_PERF_RECORD)

    # ============================ STEP 3 ============================
    output_lines = exec_command(COMMAND_MMAP, capture_output=True)
    mmap_addr = output_lines[0]

    size = re.search(r'\((.*?)\)', mmap_addr).group(1)

    base_addr = mmap_addr.split('[')[2]
    base_addr = base_addr.split('(')[0]

    base_addr_pre = base_addr[2:10]
    print(f"[mmap_addr: {mmap_addr}]\n[size: {size}]\n[base_addr: {base_addr}]\n[base_addr_pre: {base_addr_pre}]")

    # ============================ STEP 4 ============================
    insn_trace_output = exec_command(COMMAND_INSN_TRACE + f" | grep {base_addr_pre}", capture_output=True)
    idx_start = -1
    idx_end = -1

    for idx, line in enumerate(insn_trace_output):
        if "main+0x" in line:
            if idx_start == -1:
                idx_start = idx
            idx_end = idx

    prev_result = ""
    for idx in range(idx_start, idx_end):
        line = insn_trace_output[idx]
        data = line.strip().split()
        addr = '0x' + data[4]
        diff = hex(int(addr, 16) - int(base_addr, 16))
        addr = '1' + diff[2:]
        out = exec_command(COMMAND_ADDR2LINE + addr, capture_output=True)
        cur_result = out[0]
        if cur_result != prev_result:
            print(cur_result)

        prev_result = cur_result