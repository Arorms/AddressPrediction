import pandas as pd

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
    return addresses

def generate_address_segment2():
    addresses = []
    for x in range(0, 256):
        for y in range(0, 256):
            part = f"{x:02x}{y:02x}"
            stripped = part.lstrip('0') or '0'
            addr = f"2001:2:{stripped}::1"
            addresses.append(addr)
    return addresses

def generate_address_segment3():
    """3000条地址"""
    addresses = []
    return addresses

def generate_address_segment4():
    

def generate_address():
    """整合所有遍历生成地址"""
    seg1 = generate_address_segment1()       # 167936
    seg2 = generate_address_segment2()       # 65536
    seg3 = generate_address_segment3()       # 897
    seg4 = generate_address_segment4()       # 70w


    all_addrs = seg1 + seg2 + seg3 + seg4

    return all_addrs

def save_to_csv(addresses, output_file='submission.csv'):
    df = pd.DataFrame(addresses, columns=['ipv6'])
    df.to_csv(output_file, index=False, header=False)
    print(f"结果已保存到 {output_file}, 共 {len(addresses)} 条地址")

if __name__ == '__main__':
    addresses = generate_address()
    save_to_csv(addresses)
