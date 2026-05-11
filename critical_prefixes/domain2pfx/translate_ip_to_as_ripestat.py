import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm  # For progress bar
import sys
import glob
import os

# Reads all JSON files in a directory
def read_all_json_files_in_a_dir(directory_path):
    return glob.glob(os.path.join(directory_path, '*.json'))

# Writes content to a JSON file
def write_json(jsonfilename, content):
    with open(jsonfilename, 'w') as fp:
        json.dump(content, fp, indent=4)

# Reads content of JSON file and returns
def read_json(jsonfilename):
    with open(jsonfilename, 'r') as jsonfile:
        return json.load(jsonfile)

# Retrieve IP prefix using RIPEstat API
def get_asn_ripe_stat(ip_address):
    try:
        url = f"https://stat.ripe.net/data/network-info/data.json?resource={ip_address}"
        response = requests.get(url, timeout=10)  # Set a timeout for quicker error handling
        data = response.json()
        return data['data'].get('asns')
    except Exception:
        return None

# Function to process a single domain's IPs and collect ASNs
def process_domain(domain, ips):
    asns = set()
    for ip in ips:
        asn_data = get_asn_ripe_stat(ip)
        if asn_data:
            asns.update(asn_data)
    return domain, list(asns)  # Return the domain and the list of unique ASNs

# Save results to JSON for Hardenize.
def save_results_hardenize(domain2asn, dataset, country_dataset):
    write_json(f"../output/{dataset}_parsed/asns_per_country/{country_dataset}_domain2asn.json", domain2asn)


if __name__ == '__main__':
    # Specify dataset
    if len(sys.argv) > 1:
        dataset = sys.argv[1]
    else:
        print("Usage: python translate_ip_to_asn.py <dataset>")
        print("Available datasets: basisbeveiliging, hardenize")
        sys.exit(1)
    
    # Load domain-to-IP mappings
    if dataset == "basisbeveiliging":
        domain2ip = read_json(f"../output/{dataset}_parsed/domain2ip.json")
        domain2asn = dict()

        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(process_domain, domain, ips): domain for domain, ips in domain2ip.items()}

            for future in tqdm(as_completed(futures), total=len(futures), desc="Processing Domains"):
                domain, asns = future.result()
                domain2asn[domain] = asns

        write_json(f"../output/{dataset}_parsed/domain2asn.json", domain2asn)
    elif dataset == "hardenize":
        domain2ip = {}
        all_json_files_hardenize = read_all_json_files_in_a_dir("../output/hardenize_parsed/ips_per_country/")

        for json_file in all_json_files_hardenize:
            country_dataset = json_file.split("ips_per_country/")[1].split("_domain2ip.json")[0]
            domain2ip[country_dataset] = read_json(json_file)

        for country_dataset, domains in domain2ip.items():
            domain2asn = {}

            with ThreadPoolExecutor() as executor:
                futures = {executor.submit(process_domain, domain, ips): domain for domain, ips in domains.items()}

                for future in tqdm(as_completed(futures), total=len(futures), desc=f"Processing {country_dataset}"):
                    domain, asns = future.result()
                    domain2asn[domain] = asns

            save_results_hardenize(domain2asn, dataset, country_dataset)
    else:
        raise ValueError("Invalid dataset. Choose 'basisbeveiliging', 'tranco', or 'hardenize'.")

