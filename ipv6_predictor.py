import re
import pandas as pd
from collections import defaultdict
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

def load_data(file_paths):
    """加载四个网段的种子地址数据"""
    data = defaultdict(list)
    for i, path in enumerate(file_paths, 1):
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    data[f'2001:{i}:'].append(line)
    return data

def extract_features(ipv6):
    """从IPv6地址中提取特征"""
    # 初始化固定长度的特征向量
    features = {
        'hex_0_len': 0,
        'hex_1_len': 0,
        'hex_2_len': 0,
        'hex_0_first': 0,
        'hex_1_first': 0,
        'hex_2_first': 0,
        'num_min': 0,
        'num_max': 0,
        'has_suffix': 0
    }
    
    parts = ipv6.split(':')
    
    # 十六进制部分分析
    hex_parts = [p for p in parts if p and not p.isdigit()]
    for i, part in enumerate(hex_parts[:3]):  # 最多分析前3个十六进制部分
        features[f'hex_{i}_len'] = len(part)
        # 将首字符转换为ASCII码值作为特征
        features[f'hex_{i}_first'] = ord(part[0].lower()) if part else 0
    
    # 数字部分分析
    num_parts = [int(p) for p in parts if p.isdigit()]
    if num_parts:
        features['num_min'] = min(num_parts)
        features['num_max'] = max(num_parts)
    
    # 后缀特征
    features['has_suffix'] = 1 if parts[-1] != '1' else 0
    
    return list(features.values())  # 返回固定长度的特征列表

def train_model(data):
    """训练预测模型"""
    # 准备训练数据
    X = []
    y = []
    for prefix, addresses in data.items():
        for addr in addresses:
            features = extract_features(addr)
            X.append(features)  # 现在features已经是固定长度的列表
            y.append(prefix)
    
    # 训练随机森林分类器
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)
    return model

def generate_address(model, num_samples=1000000):
    """生成预测地址"""
    # 这里简化实现，实际应根据模型预测生成
    generated = []
    patterns = {
        '2001:1:': lambda: f"2001:1:{np.random.choice(['a','b','c','d','e','f'])}{hex(np.random.randint(0, 16))[2:]}{hex(np.random.randint(0, 16))[2:]}:{np.random.randint(1, 41)}::1",
        '2001:2:': lambda: f"2001:2:{hex(np.random.randint(0, 65536))[2:]}::1",
        '2001:3:': lambda: np.random.choice([
            f"2001:3:f0aa:1fa::{np.random.choice([1,3])}",
            f"2001:3:bac::cccc:{np.random.randint(8, 11)}",
            f"2001:3:0:bac1::ccdd:{np.random.choice([2,5])}"
        ]),
        '2001:4:': lambda: np.random.choice([
            f"2001:4:{hex(np.random.randint(0, 65536))[2:]}::{hex(np.random.randint(0, 4096))[2:]}",
            f"2001:4:{hex(np.random.randint(0, 65536))[2:]}:1000::{hex(np.random.randint(0, 4096))[2:]}"
        ])
    }
    
    # 按比例生成四个网段的地址
    for _ in range(num_samples):
        prefix = np.random.choice(list(patterns.keys()), p=[0.25, 0.25, 0.25, 0.25])
        generated.append(patterns[prefix]())
    
    return generated

def save_to_csv(addresses, output_file='submission.csv'):
    """保存结果到CSV文件"""
    df = pd.DataFrame(addresses, columns=['ipv6'])
    df.to_csv(output_file, index=False, header=False)
    print(f"结果已保存到 {output_file}")

if __name__ == '__main__':
    # 数据文件路径
    file_paths = [
        'give_data/1_give.txt',
        'give_data/2_give.txt', 
        'give_data/3_give.txt',
        'give_data/4_give.txt'
    ]
    
    # 1. 加载数据
    data = load_data(file_paths)
    
    # 2. 训练模型
    model = train_model(data)
    joblib.dump(model, 'ipv6_model.pkl')
    
    # 3. 生成预测地址
    addresses = generate_address(model, 1000000)
    
    # 4. 保存结果
    save_to_csv(addresses)
