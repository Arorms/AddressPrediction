addresses = []
seeds = open('4_short_1000.txt').readlines()
seed_prefixes = {":".join(addr.strip().split(":")[:3]) for addr in seeds}
seed_suffixes = {
    part for addr in seeds
    if len(addr.strip().split(":")[-1]) == 3
    for part in [addr.strip().split(":")[-1]]
}

for prefix in seed_prefixes:
    for surfix in seed_suffixes:
        addresses.append(f"{prefix}:1000::{surfix}")

open('subnet4_predict.txt', 'w').write('\n'.join(addresses))
