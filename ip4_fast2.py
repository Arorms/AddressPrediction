import ipaddress, random, pandas as pd
from collections import Counter, defaultdict

SEED = 'give_data/4_give.txt'
OUT  = 'submission.csv'
MAX_SUBMIT = 495_000
BAND       = 32      # 连续块带宽
STEP_MAX   = 512
LOW_XOR    = 0x3FF
PREF_QUOTA = 634
PREF_QUOTA_0000 = 400

# 1. 读取
seeds = [l.strip() for l in open(SEED) if l.strip()]
seed_set = set(seeds)
cnt64, tails = Counter(), defaultdict(list)

for a in seeds:
    p = ipaddress.IPv6Address(a).exploded.split(':')
    pre64 = ':'.join(p[:4])
    cnt64[pre64] += 1
    tails[pre64].append(int(ipaddress.IPv6Address(a)) & 0xFFFFFFFF)

# 2. 选热门 /64
hot64 = [pre for pre,c in cnt64.most_common(900) if c >= 1]

submit = set()
def add(pre, val):
    suf = f'{val & 0xFFFF:x}' if val>>16 == 0 else f'{val>>16:x}:{val&0xFFFF:04x}'
    addr = f'{pre}::{suf}'
    comp = ipaddress.IPv6Address(addr).compressed
    if comp not in seed_set:
        submit.add(comp)

# 3. 生成
for pre in hot64:
    quota = PREF_QUOTA_0000 if pre.endswith(':0000') else PREF_QUOTA
    gen = 0
    base = sorted(set(tails[pre]))
    # A. 连续块
    blocks = []
    cur = [base[0]]
    for t in base[1:]:
        if t - cur[-1] <= BAND:
            cur.append(t)
        else:
            blocks.append(cur); cur=[t]
    blocks.append(cur)
    for blk in blocks:
        for v in range(max(0,blk[0]-BAND), min(blk[-1]+BAND+1, 0x100000000)):
            add(pre, v); gen+=1
            if gen>=quota or len(submit)>=MAX_SUBMIT: break
        if gen>=quota or len(submit)>=MAX_SUBMIT: break
    if gen>=quota or len(submit)>=MAX_SUBMIT: continue
    # B. 步长
    diffs = [b-a for a,b in zip(base, base[1:])]
    if diffs:
        step = Counter(diffs).most_common(1)[0][0]
        if step in (16,32,256):
            for x in base:
                nxt = x + step
                for _ in range(STEP_MAX):
                    if nxt>=0x100000000: break
                    add(pre, nxt); gen+=1
                    if gen>=quota or len(submit)>=MAX_SUBMIT: break
                    nxt += step
                if gen>=quota or len(submit)>=MAX_SUBMIT: break
    if gen>=quota or len(submit)>=MAX_SUBMIT: continue
    # C. 低位 XOR
    for x in base[:min(50,len(base))]:
        for _ in range(256):
            add(pre, x ^ random.randint(0, LOW_XOR)); gen+=1
            if gen>=quota or len(submit)>=MAX_SUBMIT: break
        if gen>=quota or len(submit)>=MAX_SUBMIT: break
    if len(submit)>=MAX_SUBMIT: break

# 4. 输出
pd.Series(sorted(submit)[:MAX_SUBMIT]).to_csv(OUT,
    index=False, header=False, encoding='utf-8')
print('生成行数:', len(submit))