import re
import pandas as pd
from collections import defaultdict
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

def generate_address_segment1():
    """生成网段 2001:1: 的所有合法地址，共 4096 * 41 = 167936 条"""
    addresses = []
    for x in range(0x000, 0x1000):  # 000 ~ fff
        hex_part = f'a{x:03x}'  # 例如 a000, a001, ..., afff
        for y in range(0, 41):  # 包含 y=0（省略）
            if y == 0:
                addr = f"2001:1:{hex_part}::1"  # 省略掉中间的 :0
            else:
                addr = f"2001:1:{hex_part}:{y}::1"
            addresses.append(addr)
    return addresses

def generate_address_segment3():
    """生成网段 2001:3: 的所有合法地址，共 3 * 299 = 897 条"""
    addresses = []
    for i in range(1, 300):  # 1~99
        addresses.append(f"2001:3:f0aa:1fa::{i}")
        addresses.append(f"2001:3:bac::cccc:{i}")
        addresses.append(f"2001:3:0:bac1::ccdd:{i}")
    return addresses


def generate_address(num_samples_other=1000000):
    """生成预测地址，部分网段固定遍历，部分使用随机策略"""
    generated = []

    # 1. 生成 2001:1: 网段（遍历）
    generated.extend(generate_address_segment1())  # 167936 条

    # 2. 生成 2001:3: 网段（遍历）
    generated.extend(generate_address_segment3())  # 897 条

    # 3. 其余网段（2001:2: 和 2001:4:）随机生成，补足数量
    remaining = num_samples_other - len(generated)
    patterns = {
        '2001:2:': lambda: f"2001:2:{hex(np.random.randint(0, 65536))[2:]}::1",
        '2001:4:': lambda: np.random.choice([
            f"2001:4:{hex(np.random.randint(0, 65536))[2:]}::{hex(np.random.randint(0, 4096))[2:]}",
            f"2001:4:{hex(np.random.randint(0, 65536))[2:]}:1000::{hex(np.random.randint(0, 4096))[2:]}"
        ])
    }

    for _ in range(remaining):
        prefix = np.random.choice(list(patterns.keys()), p=[0.5, 0.5])
        generated.append(patterns[prefix]())

    return generated



def save_to_csv(addresses, output_file='submission.csv'):
    """保存结果到CSV文件"""
    df = pd.DataFrame(addresses, columns=['ipv6'])
    df.to_csv(output_file, index=False, header=False)
    print(f"结果已保存到 {output_file}")

if __name__ == '__main__':

    addresses = generate_address(1000000 - 167936 - 897)
    
    save_to_csv(addresses)
