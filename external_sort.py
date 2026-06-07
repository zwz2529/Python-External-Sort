import sys
import os
import struct
import tempfile
import heapq
import multiprocessing
from array import array
# 工作进程：负责对数据块进行快速排序 (利用多核)
def sort_chunk(args):
    temp_file_path, chunk_size = args
    arr = array('i')  # 'i' 代表 32位有符号整数

    with open(temp_file_path, 'rb') as f:
        try:
            arr.fromfile(f, chunk_size)
        except EOFError:
            pass

            # 在内存中进行排序 (O(n log n) 复杂度)
    arr = sorted(arr)
    sorted_arr = array('i', arr)

    # 覆写回临时文件
    with open(temp_file_path, 'wb') as f:
        sorted_arr.tofile(f)

    return temp_file_path
# 生成器：逐个读取二进制整数，极低内存占用
def read_ints_from_file(file_path):
    with open(file_path, 'rb') as f:
        while True:
            bytes_read = f.read(4)  # 32位 = 4 bytes
            if not bytes_read or len(bytes_read) < 4:
                break
            yield struct.unpack('<i', bytes_read)[0]
# 主程序：拆分 -> 多进程排序 -> 多路归并
def external_sort(input_file, chunk_size):
    output_file = input_file + ".sorted.bin"
    bytes_per_chunk = chunk_size * 4
    temp_dir = tempfile.mkdtemp()

    print(f"1. 正在拆分文件并分配给 {multiprocessing.cpu_count()} 个 CPU 核心进行排序...")
    chunk_args = []
    with open(input_file, 'rb') as f:
        chunk_idx = 0
        while True:
            chunk_data = f.read(bytes_per_chunk)
            if not chunk_data:
                break
            temp_path = os.path.join(temp_dir, f"chunk_{chunk_idx}.bin")
            with open(temp_path, 'wb') as tf:
                tf.write(chunk_data)
            chunk_args.append((temp_path, chunk_size))
            chunk_idx += 1

    # 使用多进程池进行并行排序
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        sorted_temp_files = pool.map(sort_chunk, chunk_args)

    print("2. 正在使用最小堆(Min-Heap)合并已排序的临时文件...")
    generators = [read_ints_from_file(tf) for tf in sorted_temp_files]

    # 写入最终结果
    with open(output_file, 'wb') as out_f:
        for val in heapq.merge(*generators):
            out_f.write(struct.pack('<i', val))

    # 清理临时文件
    for tf in sorted_temp_files:
        os.remove(tf)
    os.rmdir(temp_dir)
    print(f"排序完成！已生成排序后的文件: {output_file}")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("用法: python external_sort.py <文件名> <允许加载的整数数量>")
        sys.exit(1)

    input_file = sys.argv[1]
    chunk_size = int(sys.argv[2])
    external_sort(input_file, chunk_size)