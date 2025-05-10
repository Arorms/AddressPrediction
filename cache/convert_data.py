import ipaddress

def expand_ipv6(ipv6_address):
    """Expands a potentially shortened IPv6 address to its full 128-bit representation."""
    try:
        ip_obj = ipaddress.IPv6Address(ipv6_address)
        return ip_obj.exploded
    except ipaddress.AddressValueError:
        return None

def read_and_expand_ipv6_to_file(input_file_path, output_file_path):
    """Reads IPv6 addresses from an input file, expands them, and saves them to an output file."""
    expanded_addresses = []
    try:
        with open(input_file_path, 'r') as infile:
            for line in infile:
                ipv6 = line.strip()
                expanded = expand_ipv6(ipv6)
                if expanded:
                    expanded_addresses.append(expanded)
                else:
                    print(f"Warning: Could not expand invalid IPv6 address: {ipv6}")

        with open(output_file_path, 'w') as outfile:
            for ip in expanded_addresses:
                outfile.write(ip + '\n')

        print(f"Successfully expanded IPv6 addresses and saved them to: {output_file_path}")

    except FileNotFoundError:
        print(f"Error: Input file not found at {input_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    input_file = "give_data/4_give.txt"  # Replace with the path to your input file
    output_file = "expanded_ipv6_addresses.txt"  # Replace with the desired output file name
    read_and_expand_ipv6_to_file(input_file, output_file)