import re
import pandas as pd
from collections import defaultdict
from tqdm import tqdm

def load_seeds(file_path):
    """加载种子地址"""
    with open(file_path) as f:
        return [line.strip() for line in f if line.strip()]

def analyze_patterns(addresses):
    """分析地址模式"""
    patterns = defaultdict(int)
    field_stats = [defaultdict(int) for _ in range(6)]  # 各字段统计
    
    for addr in tqdm(addresses, desc="Analyzing patterns"):
        fields = addr.split(':')
        # 统计各字段值
        for i, field in enumerate(fields[:6]):
            if field:
                field_stats[i][field] += 1
        # 记录整体模式
        pattern = ':'.join(fields[:4])
        patterns[pattern] += 1
    
    return patterns, field_stats

def generate_1000_addresses(seeds, count=70000):
    """生成1000类地址"""
    prefixes = {":".join(addr.split(':')[:3]) for addr in seeds if ':1000::' in addr}
    suffixes = {addr.split(':')[-1] for addr in seeds if len(addr.split(':')[-1]) in (1,2,3,4)}
    
    addresses = []
    for prefix in prefixes:
        for suffix in suffixes:
            addresses.append(f"{prefix}:1000::{suffix}")
            if len(addresses) >= count:
                return addresses
    return addresses

def generate_other_addresses(seeds, count=30000):
    """生成其他类型地址"""
    # 分析非1000类地址模式
    other_addrs = [addr for addr in seeds if ':1000::' not in addr]
    
    # 提取常见前缀模式
    prefix_patterns = defaultdict(int)
    for addr in other_addrs:
        fields = addr.split(':')
        if len(fields) >= 4:
            prefix = ':'.join(fields[:3])
            prefix_patterns[prefix] += 1
    
    # 提取常见后缀模式
    suffix_patterns = defaultdict(int)
    for addr in other_addrs:
        suffix = addr.split(':')[-1]
        if suffix:
            suffix_patterns[suffix] += 1
    
    # 生成预测地址
    addresses = []
    top_prefixes = sorted(prefix_patterns.items(), key=lambda x: -x[1])[:10]
    top_suffixes = sorted(suffix_patterns.items(), key=lambda x: -x[1])[:20]
    
    for prefix, _ in top_prefixes:
        for suffix, _ in top_suffixes:
            addresses.append(f"{prefix}::{suffix}")
            if len(addresses) >= count:
                return addresses
    
    # 补充随机模式
    for i in range(count - len(addresses)):
        addr = f"2001:4:{i:x}::{i+100:x}"
        addresses.append(addr)
    
    return addresses[:count]

def save_predictions(addresses, output_file):
    """保存预测结果"""
    df = pd.DataFrame(addresses, columns=['ipv6'])
    df.to_csv(output_file, index=False, header=False)
    print(f"Generated {len(addresses)} predictions to {output_file}")

if __name__ == '__main__':
    seeds = load_seeds('give_data/4_give.txt')
    
    # 生成1000类地址
    addrs_1000 = generate_1000_addresses(seeds)
    
    # 生成其他地址
    addrs_other = generate_other_addresses(seeds)
    
    # 合并结果
    all_addrs = addrs_1000 + addrs_other
    
    # 保存预测
    save_predictions(all_addrs, 'submission/s4_enhanced.csv')
