import sys
import os
import struct
import tempfile
import multiprocessing
import heapq

# 对一个临时块文件进行排序（读入内存排序写回）
def sort_chunk(chunk_path):
    with open(chunk_path, 'rb') as f:
        raw = f.read()
    # 每4字节解析为一个整数
    numbers = []
    for i in range(0, len(raw), 4):
        numbers.append(struct.unpack('<i', raw[i:i+4])[0])
    numbers.sort()
    with open(chunk_path, 'wb') as f:
        for x in numbers:
            f.write(struct.pack('<i', x))

# 多路归并：将多个已排序的临时文件合并成一个输出文件
def merge_files(sorted_paths, out_path):
    # 打开所有临时文件
    files = [open(p, 'rb') for p in sorted_paths]
    heap = []
    # 读每个文件的第一个整数
    for idx, f in enumerate(files):
        buf = f.read(4)
        if buf:
            val = struct.unpack('<i', buf)[0]
            heap.append((val, idx))
    heapq.heapify(heap)

    with open(out_path, 'wb') as out:
        while heap:
            val, idx = heapq.heappop(heap)
            out.write(struct.pack('<i', val))
            # 从同一个文件读取下一个整数
            buf = files[idx].read(4)
            if buf:
                next_val = struct.unpack('<i', buf)[0]
                heapq.heappush(heap, (next_val, idx))

    for f in files:
        f.close()

def external_sort(input_file, chunk_size):
    out_file = input_file + ".sorted"
    # 创建临时目录存放块文件
    tmp_dir = tempfile.mkdtemp()
    chunk_list = []

    # 一将原文件拆分成若干块（每块最多 chunk_size 个整数）
    with open(input_file, 'rb') as fin:
        idx = 0
        while True:
            block = fin.read(chunk_size * 4)
            if not block:
                break
            tmp_path = os.path.join(tmp_dir, f"chunk_{idx}.tmp")
            with open(tmp_path, 'wb') as fout:
                fout.write(block)
            chunk_list.append(tmp_path)
            idx += 1

    # 二利用多核并行排序各个块
    cpu_num = multiprocessing.cpu_count()
    with multiprocessing.Pool(processes=cpu_num) as pool:
        pool.map(sort_chunk, chunk_list)

    # 三归并所有已排序的块
    merge_files(chunk_list, out_file)

    # 清理临时文件
    for p in chunk_list:
        os.remove(p)
    os.rmdir(tmp_dir)
    print("排序完成，结果保存在:", out_file)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("用法: python sort.py <文件名> <每批整数数量>")
        sys.exit(1)
    external_sort(sys.argv[1], int(sys.argv[2]))
