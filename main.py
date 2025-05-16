import ipaddress, random, pandas as pd
from collections import Counter, defaultdict

SEED_FILE = 'give_data/4_give.txt'
OUT_FILE = 'submission.csv'


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


def generate_address_segment4():
    def generate_1000_addresses():
        """
        生成 49 万 IPv6 预测地址：
        1. 统计 third-hextet / tail 频次
        2. 热段 × 高频尾
        3. 若未满 49 万，再顺序枚举 tail（0~0xfff）
        直到凑够 490_000 行
        """
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
        return submit_list

    def generate_other_addresses():
        MAX_SUBMIT = 495_000
        BAND       = 32      # 连续块带宽
        STEP_MAX   = 512
        LOW_XOR    = 0x3FF
        PREF_QUOTA = 634
        PREF_QUOTA_0000 = 400

        # 1. 读取
        seeds = [l.strip() for l in open(SEED_FILE) if l.strip()]
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

        return sorted(submit)
    addr = []
    addr += generate_1000_addresses()
    addr += generate_other_addresses()
    print(f"网段 4 生成了 {len(addr)} 条地址")
    return addr
    

if __name__ == '__main__':
    seg1 = generate_address_segment1()       # 167936
    seg2 = generate_address_segment2()       # 65536
    seg3 = generate_address_segment3()       # 897
    seg4 = generate_address_segment4()       # 70w

    all_addrs = seg1 + seg2 + seg3 + seg4
    
    df = pd.DataFrame(all_addrs, columns=['ipv6'])
    df.to_csv(OUT_FILE, index=False, header=False)
    print(f"结果已保存到 {OUT_FILE}, 共 {len(all_addrs)} 条地址")
    