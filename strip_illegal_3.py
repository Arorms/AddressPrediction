import ipaddress

input_file = "submission3.csv"      # 输入文件
output_file = "submission3.csv"    # 输出文件

with open(input_file, "r") as infile, open(output_file, "w") as outfile:
    for line in infile:
        ip_str = line.strip()
        try:
            ip = ipaddress.IPv6Address(ip_str)
            outfile.write(ip_str + "\n")  # 合法的 IPv6 地址写入输出文件
        except ipaddress.AddressValueError:
            pass  # 不合法则跳过
