import sys
import csv
import json
import pytricia
import glob
import os
from pprint import pprint as pprint

# Finds all JSON files in a directory
def read_all_json_files_in_a_dir(directory_path):
    return glob.glob(os.path.join(directory_path, '*.json'))

# Writes content to a json file
def write_json(jsonfilename, content):
    with open(jsonfilename, 'w+') as fp:
        json.dump(content, fp, indent=4)

# Reads content of JSON file and returns
def read_json(jsonfilename):
    with open(jsonfilename, 'r') as jsonfile:
        return json.load(jsonfile)

# Populates bogus prefixes in a pytricia tree
def create_bogons_trees(filename1, filename2):
    # Downloaded data from: https://www.team-cymru.com/bogon-reference-http
    # Create one structure for IPv4 and one for IPv6
    bogons_pyt_v4 = pytricia.PyTricia()
    bogons_pyt_v6 = pytricia.PyTricia(128)
    
    # Read bogons from Cymru website: https://www.team-cymru.com/bogon-reference 
    with open(filename1, 'r') as ipv4_bogon:
        ipv4_bog = csv.reader(ipv4_bogon)
        # Skip first and second line of CSV
        next(ipv4_bog)
        next(ipv4_bog)
        for row in ipv4_bog:
            bogus_pref = row[0]
            bogons_pyt_v4.insert(bogus_pref, 'bogus')
                    
    with open(filename2, 'r') as ipv6_bogon:
        ipv6_bog = csv.reader(ipv6_bogon)
        # Skip first and second line of CSV
        next(ipv6_bog)
        next(ipv6_bog)
        for row in ipv6_bog:
            bogus_pref = row[0]
            bogons_pyt_v6.insert(bogus_pref, 'bogus')

    return (bogons_pyt_v4, bogons_pyt_v6)

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

# Returns true if prefix is not private/unallocated/reserved
def is_valid(prefix, bogons_pyt_v4, bogons_pyt_v6):
    # First of all discard exact prefix matches from fullbogons tree
    if ((prefix in bogons_pyt_v4) or (prefix in bogons_pyt_v6)):
        return False
    
    # In all other occassions return True
    return True
   
# Populates prefixes and paths in a pytricia tree
def populate_pytricia_tree(prefixes):
    # Initialize the structures. Have two different tries for v4 and v6. See documentation!
    pyt_v4 = pytricia.PyTricia()
    pyt_v6 = pytricia.PyTricia(128)
    for prefix in prefixes:
        # Find if v4 or v6 and add to the respective tree!
        if prefix.find(':') == -1:  # v4
            # Add the prefix in the IPv4 tree
            pyt_v4.insert(prefix, prefix)
        elif prefix.find(":") > -1: # v6
            # Add the prefix in the IPv6 tree
            pyt_v6.insert(prefix, prefix)

    # Return the structures
    return (pyt_v4, pyt_v6)

# Prints a pytricia tree
def print_pytricia_tree(trie):
    for prefix in trie:
        print(f"{prefix} -> {trie[prefix]}")

# Returns the Longest Prefix Match of an IP address
def lpm(ip, pyt_v4, pyt_v6):
    # We translate the ip to ip prefix by simply adding a /32 in the end
    ip_pfx = ip + "/128" if ':' in ip else ip + "/32"
    try:
        # Then we search if this prefix is covered in one of our pytries
        if ip.find(':') == -1:
            return pyt_v4.get(ip_pfx)
        elif ip.find(':') > -1:
            return pyt_v6.get(ip_pfx)
    except Exception:
        return None

# Load the domain2ip dataset based on the specified dataset name
def load_domain2ip(dataset):
    if dataset == "basisbeveiliging" or dataset == "tranco":
        return read_json("../output/" + dataset + "_parsed/domain2ip.json")
    elif dataset == "hardenize":
        to_be_returned = dict()
        all_json_files_hardenize = read_all_json_files_in_a_dir("../output/" + dataset + "_parsed/ips_per_country/")
        for json_file in all_json_files_hardenize:
            to_be_returned[json_file.split("ips_per_country/")[1].split("_domain2ip.json")[0]] = read_json(json_file)
        return to_be_returned
    else:
        raise ValueError("Invalid dataset. Choose 'basisbeveiliging' or 'tranco'.")
    
# Save results to JSON based on dataset name.
def save_results(domain2pfx, uncovered_ips, dataset):
    if dataset == "basisbeveiliging" or dataset == 'tranco':
        write_json("../output/" + dataset + "_parsed/domain2pfx_routeviews.json", domain2pfx)
        write_json("../output/" + dataset + "_parsed/domain2pfx_routeviews_uncovered.json", uncovered_ips)

# Save results to JSON for Hardenize.
def save_results_hardenize(domain2pfx, uncovered_ips, dataset, country_dataset):
    print(country_dataset)
    if dataset == "hardenize":
        write_json("../output/" + dataset + "_parsed/prefixes_per_country/" + country_dataset + "_domain2pfx_routeviews.json", domain2pfx)
        write_json("../output/" + dataset + "_parsed/prefixes_per_country/" + country_dataset + "_domain2pfx_routeviews_uncovered.json", uncovered_ips)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        dataset = sys.argv[1] 
    else:
        print("Usage: python translate_ip_to_prefix_routeviews.py <dataset>")
        print("Available datasets: basisbeveiliging, tranco, hardenize")
        sys.exit(1)
    # Read the domain2ip dataset from Basibeveiliging or Tranco
    domain2ip = load_domain2ip(dataset)

    # Read all the public prefixes from the CAIDA pfx2as dataset
    all_public_pfxs_v4 = get_all_public_ip_prefixes('../../caida/routeviews-rv2-20241101-0400.pfx2as')
    all_public_pfxs_v6 = get_all_public_ip_prefixes('../../caida/routeviews-rv6-20241101-0000.pfx2as')
    all_public_pfxs = all_public_pfxs_v4 + all_public_pfxs_v6

    # Populate the prefixes in a pytricia tree discarding bogons/private/unallocated prefixes
    pyt_v4, pyt_v6 = populate_pytricia_tree(all_public_pfxs)

    # Create a domain to prefix dictionary using the above datasets
    if dataset == "hardenize":
        for country_dataset in domain2ip:
            uncovered_ips = dict()
            domain2pfx = dict()
            for idx, domain in enumerate(domain2ip[country_dataset]):
                # print('Mapping Domains to Prefixes {:.5}%\r'.format(idx * 100/len(domain2ip)), end='')
                domain2pfx[domain] = list()
                for ip in domain2ip[country_dataset][domain]:
                    pfx = lpm(ip, pyt_v4, pyt_v6)
                    if not pfx:
                        if domain not in uncovered_ips:
                            uncovered_ips[domain] = list()
                        if ip not in uncovered_ips[domain]:
                            uncovered_ips[domain].append(ip)
                    if pfx and pfx not in domain2pfx[domain]:
                        domain2pfx[domain].append(pfx)
            save_results_hardenize(domain2pfx, uncovered_ips, dataset, country_dataset)
    else:
        uncovered_ips = dict()
        domain2pfx = dict()
        for idx, domain in enumerate(domain2ip):
            # print('Mapping Domains to Prefixes {:.5}%\r'.format(idx * 100/len(domain2ip)), end='')
            domain2pfx[domain] = list()
            for ip in domain2ip[domain]:
                pfx = lpm(ip, pyt_v4, pyt_v6)
                if not pfx:
                    if domain not in uncovered_ips:
                        uncovered_ips[domain] = list()
                    if ip not in uncovered_ips[domain]:
                        uncovered_ips[domain].append(ip)
                if pfx and pfx not in domain2pfx[domain]:
                    domain2pfx[domain].append(pfx)

        # Save results to appropriate JSON files
        save_results(domain2pfx, uncovered_ips, dataset)
    
