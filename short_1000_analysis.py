import matplotlib.pyplot as plt
import re

seeds_1000 = open('4_short_1000.txt').readlines()

pattern = re.compile(r"^2001:4:3b72")

filtered_seeds = [addr.strip() for addr in seeds_1000 if pattern.match(addr)]

seed_surfixes = {addr.strip().split(":")[-1] for addr in filtered_seeds}
count = sum(1 for _ in seed_surfixes)

pattern = re.compile(r"^2001:4:3b71")

filtered_suffixes = [s for s in seed_surfixes]

print(f"Filtered suffixes (length 1): {filtered_suffixes}")

suffix_values = sorted([int(s, 16) for s in filtered_suffixes])

# suffix_values = [s for s in suffix_values if s > 16400]

print(max(suffix_values))

# 绘制走势图
plt.figure(figsize=(10, 4))
plt.plot(suffix_values, marker='o', linestyle='-')
plt.title("Trend of IPv6 Suffixes")
plt.xlabel("Index")
plt.ylabel("Decimal Value of Suffix")
plt.grid(True)
plt.tight_layout()
plt.show()