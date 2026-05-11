from pprint import pprint as pprint
import csv
import json
import random

# Writes content to a json file
def write_json(jsonfilename, content):
    with open(jsonfilename, 'w+') as fp:
        json.dump(content, fp, indent=4)
        
# Returns a list with all public prefixes
def get_all_public_ip_prefixes(url):
    # Initialize an empty list to store the BGP prefixes as strings
    bgp_prefixes = []
    # Read the file
    with open(url, 'r') as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            ip = row[0]
            prefix_length = row[1]
            
            # Create the BGP prefix in the format 'IP/prefix_length'
            bgp_prefix = f"{ip}/{prefix_length}"
            
            # Append only the BGP prefix string
            bgp_prefixes.append(bgp_prefix)
    return bgp_prefixes      

if __name__ == '__main__':
    RANDOM_SAMPLE = 1000
    # Read all the public prefixes from the CAIDA pfx2as dataset
    all_public_pfxs_v4 = get_all_public_ip_prefixes('routeviews-rv2-20241101-0400.pfx2as')
    all_public_pfxs_v6 = get_all_public_ip_prefixes('routeviews-rv6-20241101-0000.pfx2as')
    all_public_pfxs = all_public_pfxs_v4 + all_public_pfxs_v6
    write_json("random_" + str(RANDOM_SAMPLE) + "_prefixes.json", random.sample(all_public_pfxs, RANDOM_SAMPLE))