import os
import re
import argparse

def extract_hostnames_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        data = file.read()

    hostnames = re.findall(r'\[(.*?)\]', data)
    return hostnames

def main(root_domain, output_file):
    directory = r'D:\Bug Bounty\Cloud\sni-ip-ranges'
    subdomains_set = set()  # Use a set to collect unique subdomains

    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory, filename)
            hostnames = extract_hostnames_from_file(file_path)
            for hostname in hostnames:
                subdomains = hostname.split()
                for subdomain in subdomains:
                    if subdomain.endswith(f".{root_domain}"):
                        subdomains_set.add(subdomain)  # Add to the set

    # Sort the unique subdomains
    sorted_subdomains = sorted(subdomains_set)

    # Print to console
    for subdomain in sorted_subdomains:
        print(subdomain)

    # Save to the specified output file
    with open(output_file, 'w') as out_file:
        for subdomain in sorted_subdomains:
            out_file.write(subdomain + '\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract and filter subdomains by root domain")
    parser.add_argument("-d", "--domain", required=True, help="Root domain (e.g., example.com)")
    parser.add_argument("-o", "--output", required=True, help="Output file")

    args = parser.parse_args()
    root_domain = args.domain
    output_file = args.output

    main(root_domain, output_file)
