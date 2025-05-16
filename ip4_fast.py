"""
生成 49 万 IPv6 预测地址：
1. 统计 third-hextet / tail 频次
2. 热段 × 高频尾
3. 若未满 49 万，再顺序枚举 tail（0~0xfff）
   直到凑够 490_000 行
"""
# 3.3分 49w
import ipaddress, random, pandas as pd
from collections import Counter

SEED_FILE   = 'give_data/4_give.txt'
OUT_FILE    = 'submission.csv'
MAX_LINES   = 490_000
THIRD_MIN   = 10       # third-hextet 出现 ≥20 次即保留（可调）
TAIL_HOT_N  = 500      # 取 tail 出现次数 Top-500 先组合（可调）
TAIL_ENUM_UPPER = 0xFFF  # 不足时枚举 0~0xFFF（含），4 位内

# ---------- 读入种子 ----------
with open(SEED_FILE, encoding='utf-8') as f:
    seeds = [ln.strip() for ln in f if ln.strip()]
seed_set = set(seeds)

# ---------- 统计 ----------
third_cnt, tail_cnt = Counter(), Counter()
for addr in seeds:
    parts = addr.split(':')
    third_cnt[parts[2]] += 1
    tail_cnt[addr.split('::')[-1] or '0'] += 1

# ---------- 生成 hot 列表 ----------
hot_thirds = [t for t,c in third_cnt.items() if c >= THIRD_MIN]
hot_tails  = [t for t,_ in tail_cnt.most_common(TAIL_HOT_N)]

submit = set()

def add(addr):
    """压缩后加入集合"""
    addr = ipaddress.IPv6Address(addr).compressed
    if addr not in seed_set:
        submit.add(addr)

# A. 热段 × 高频尾
for t3 in hot_thirds:
    for tail in hot_tails:
        add(f'2001:4:{t3}:1000::{tail}')
        if len(submit) >= MAX_LINES:
            break
    if len(submit) >= MAX_LINES:
        break

# B. 若数量不足，用顺序或随机枚举 tail 补齐
if len(submit) < MAX_LINES:
    # 可以随机洗牌 third 列表，避免集中
    random.shuffle(hot_thirds)
    for t3 in hot_thirds:
        for tail_int in range(TAIL_ENUM_UPPER + 1):  # 0x0 ~ 0xfff
            tail = format(tail_int, 'x')             # 十六进制无前导零
            add(f'2001:4:{t3}:1000::{tail}')
            if len(submit) >= MAX_LINES:
                break
        if len(submit) >= MAX_LINES:
            break


submit_list = sorted(submit)[:MAX_LINES]           # 保证不超
pd.Series(submit_list).to_csv(OUT_FILE,
                              index=False, header=False, encoding='utf-8')
print(f'生成 {len(submit_list):,} 条地址 → {OUT_FILE}')
