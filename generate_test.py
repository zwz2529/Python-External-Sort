import random
import struct

def gen(fn, cnt):
    print("正在生成", cnt, "个随机整数...")
    f = open(fn, "wb")
    for _ in range(cnt):
        v = random.randint(-2147483648, 2147483647)
        f.write(struct.pack("<i", v))
    f.close()
    print("完成！")

gen("test_data.bin", 1000000)
