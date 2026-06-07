import sys
import os
import struct
import tempfile
import multiprocessing
import heapq

# 排序一个临时块
def s(path):
    f = open(path, 'rb')
    d = f.read()
    f.close()
    a = []
    for i in range(0, len(d), 4):
        a.append(struct.unpack('<i', d[i:i+4])[0])
    a.sort()
    f2 = open(path, 'wb')
    for x in a:
        f2.write(struct.pack('<i', x))
    f2.close()

# 合并所有临时文件
def m(tmp, out):
    fs = []
    for p in tmp:
        fs.append(open(p, 'rb'))
    h = []
    for i, f in enumerate(fs):
        b = f.read(4)
        if b:
            v = struct.unpack('<i', b)[0]
            h.append((v, i))
    heapq.heapify(h)
    o = open(out, 'wb')
    while h:
        v, i = heapq.heappop(h)
        o.write(struct.pack('<i', v))
        b2 = fs[i].read(4)
        if b2:
            v2 = struct.unpack('<i', b2)[0]
            heapq.heappush(h, (v2, i))
    o.close()
    for f in fs:
        f.close()

def run(fname, size):
    out_file = fname + ".sorted"
    tmp_dir = tempfile.mkdtemp()
    tmp_files = []
    # 拆分
    with open(fname, 'rb') as fin:
        cnt = 0
        while True:
            block = fin.read(size * 4)
            if not block:
                break
            p = os.path.join(tmp_dir, "t" + str(cnt) + ".bin")
            with open(p, 'wb') as fout:
                fout.write(block)
            tmp_files.append(p)
            cnt += 1
    # 并行排序
    cpu_n = multiprocessing.cpu_count()
    with multiprocessing.Pool(processes=cpu_n) as pool:
        pool.map(s, tmp_files)
    # 合并
    m(tmp_files, out_file)
    # 清理
    for p in tmp_files:
        os.remove(p)
    os.rmdir(tmp_dir)
    print("搞定，结果:", out_file)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("用: python sorter.py <文件> <每次个数>")
        sys.exit(1)
    run(sys.argv[1], int(sys.argv[2]))
