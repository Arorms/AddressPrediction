import ipaddress, random, pandas as pd
from collections import Counter, defaultdict

SEED_FILE = 'give_data/4_give.txt'
OUT_FILE = 'submission12.csv'


def generate_address_segment1():
    addresses = []
    for x in range(0x000, 0x1000):  # 000 ~ fff
        hex_part = f'a{x:03x}'
        for y in range(0, 41):
            if y == 0:
                addr = f"2001:1:{hex_part}::1"
            else:
                addr = f"2001:1:{hex_part}:{y}::1"
            addresses.append(addr)
            
    print(f"网段 1 生成了 {len(addresses)} 条地址")
    return addresses


def generate_address_segment2():
    addresses = []
    for x in range(0, 256):
        for y in range(0, 256):
            part = f"{x:02x}{y:02x}"
            stripped = part.lstrip('0') or '0'
            addr = f"2001:2:{stripped}::1"
            addresses.append(addr)
            
    print(f"网段 2 生成了 {len(addresses)} 条地址")
    return addresses


def generate_address_segment3():
    """3000条地址"""
    addresses = []
    
    print(f"网段 3 生成了 {len(addresses)} 条地址")
    return addresses


if __name__ == '__main__':
    seg1 = generate_address_segment1()       # 167936
    seg2 = generate_address_segment2()       # 65536

    all_addrs = seg1 + seg2
    
    df = pd.DataFrame(all_addrs, columns=['ipv6'])
    df.to_csv(OUT_FILE, index=False, header=False)
    print(f"结果已保存到 {OUT_FILE}, 共 {len(all_addrs)} 条地址")
    