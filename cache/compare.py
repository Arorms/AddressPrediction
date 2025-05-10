# seeds = open("give_data/4_give.txt").readlines()
seeds = open("4_short_1000.txt").readlines()

seed_prefixes = {":".join(addr.strip().split(":")[:3]) for addr in seeds}

sub = open("cache/zq_sub_4.csv").readlines()

sub_prefixes = {":".join(addr.strip().split(":")[:3]) for addr in sub}

for sub_prefix in sorted(sub_prefixes):
    if sub_prefix in seed_prefixes:
        print(sub_prefix)