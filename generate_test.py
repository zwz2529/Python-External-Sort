import random
import struct

def create_random_bin(filename, num_ints):
    print(f"正在生成包含 {num_ints} 个随机整数的测试文件...")
    with open(filename, 'wb') as f:
        for _ in range(num_ints):
            val = random.randint(-2147483648, 2147483647)
            f.write(struct.pack('<i', val))
    print("生成完毕！")

# 生成100万个数字的文件测试用
create_random_bin("test_data.bin", 1000000)