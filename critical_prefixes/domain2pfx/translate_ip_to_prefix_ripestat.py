import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm  # Import tqdm for progress bar

# Writes content to a JSON file
def write_json(jsonfilename, content):
    with open(jsonfilename, 'w') as fp:
        json.dump(content, fp, indent=4)

# Reads content of JSON file and returns
def read_json(jsonfilename):
    with open(jsonfilename, 'r') as jsonfile:
        return json.load(jsonfile)

# Retrieve IP prefix using RIPEstat API
def get_ip_prefix_ripe_stat(ip_address):
    try:
        url = f"https://stat.ripe.net/data/network-info/data.json?resource={ip_address}"
        response = requests.get(url, timeout=5)  # Set a timeout for quicker error handling
        data = response.json()
        return data['data'].get('prefix')
    except Exception:
        return None

def resolve_ip_prefixes(domain2ip):
    domain2pfx = {}
    uncovered_ips = {}
    ip_cache = {}

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_domain_ip = {}

        # Schedule all requests concurrently and count total IPs
        total_ips = sum(len(ips) for ips in domain2ip.values())
        for domain, ips in domain2ip.items():
            domain2pfx[domain] = []
            for ip in ips:
                if ip in ip_cache:  # Use cached result if available
                    pfx = ip_cache[ip]
                    if pfx:
                        domain2pfx[domain].append(pfx)
                    else:
                        uncovered_ips.setdefault(domain, []).append(ip)
                else:
                    future = executor.submit(get_ip_prefix_ripe_stat, ip)
                    future_to_domain_ip[future] = (domain, ip)

        # Process completed futures with a progress bar
        with tqdm(total=total_ips, desc="Resolving IP Prefixes") as pbar:
            for future in as_completed(future_to_domain_ip):
                domain, ip = future_to_domain_ip[future]
                pfx = future.result()

                # Cache the result
                ip_cache[ip] = pfx

                if pfx:
                    if pfx not in domain2pfx[domain]:
                        domain2pfx[domain].append(pfx)
                else:
                    uncovered_ips.setdefault(domain, []).append(ip)

                pbar.update(1)  # Update the progress bar

    return domain2pfx, uncovered_ips

if __name__ == '__main__':
    # Load domain-to-IP mappings
    domain2ip = read_json('../output/basisbeveiliging_parsed/domain2ip.json')

    # Resolve IP prefixes
    domain2pfx, uncovered_ips = resolve_ip_prefixes(domain2ip)

    # Write results to JSON files
    write_json("../output/basisbeveiliging_parsed/domain2pfx_ripestat.json", domain2pfx)
    write_json("../output/basisbeveiliging_parsed/domain2pfx_ripestat_uncovered.json", uncovered_ips)
