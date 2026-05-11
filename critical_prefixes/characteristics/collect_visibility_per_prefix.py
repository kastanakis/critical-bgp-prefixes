import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm  # Import tqdm for progress bars

# Writes content to a JSON file
def write_json(jsonfilename, content):
    with open(jsonfilename, 'w') as fp:
        json.dump(content, fp, indent=4)

# Reads content of JSON file and returns
def read_json(jsonfilename):
    with open(jsonfilename, 'r') as jsonfile:
        return json.load(jsonfile)

def calculate_visibility(data):
    """
    Automatically calculate the visibility percentage based on RIS data for either IPv4 or IPv6.
    """
    if 'ipv4_full_table_peer_count' in data and data['ipv4_full_table_peer_count'] > 0:
        total_peers_v4 = data['ipv4_full_table_peer_count']
        peers_seeing_v4 = len(data.get('ipv4_full_table_peers_seeing', []))
        return (peers_seeing_v4 / total_peers_v4) * 100

    if 'ipv6_full_table_peer_count' in data and data['ipv6_full_table_peer_count'] > 0:
        total_peers_v6 = data['ipv6_full_table_peer_count']
        peers_seeing_v6 = len(data.get('ipv6_full_table_peers_seeing', []))
        return (peers_seeing_v6 / total_peers_v6) * 100

    return 0

def fetch_visibility_data(resource):
    """
    Fetch visibility data from the RIPE API for a given resource.
    """
    url = "https://stat.ripe.net/data/visibility/data.json"
    params = {
        "data_overload_limit": "ignore",
        "include": "peers_seeing",
        "resource": resource
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from RIPE API for {resource}: {e}")
        return None

def process_visibility_for_prefix(prefix):
    """
    Process visibility data for a single prefix and calculate average visibility.
    """
    visibility_data = fetch_visibility_data(prefix)
    if visibility_data and 'data' in visibility_data and 'visibilities' in visibility_data['data']:
        sum_visibility = 0
        visibilities = visibility_data['data']['visibilities']
        
        for rc_records in visibilities:
            sum_visibility += calculate_visibility(rc_records)
        
        return sum_visibility / len(visibilities) if visibilities else 0
    return 0

if __name__ == "__main__":
    random_1000_prefixes = read_json("../../caida/random_1000_prefixes.json")
    
    random_prefix2visibility = {}
    # Process each prefix across all domains with a single progress bar
    with ThreadPoolExecutor(max_workers=10) as executor, tqdm(total=len(random_1000_prefixes), desc="Processing Prefixes") as pbar:
        future_to_prefix = {
            executor.submit(process_visibility_for_prefix, prefix): prefix for prefix in random_1000_prefixes
        }

        # Collect results as they complete
        for future in as_completed(future_to_prefix):
            prefix = future_to_prefix[future]
            average_visibility = future.result()

            # Update the result dictionary
            if prefix not in random_prefix2visibility:
                random_prefix2visibility[prefix] = {}
            random_prefix2visibility[prefix] = average_visibility
            
            # Update progress bar
            pbar.update(1)
    write_json("../output/characteristics/visibility/random_1000_prefixes2visibility.json", random_prefix2visibility)
    
    domain2pfx_inputs = [("../output/hardenize_parsed/prefixes_per_country/bahamas-web-hygiene-dashboard_domain2pfx_routeviews.json", "bahamas"),\
                        ("../output/hardenize_parsed/prefixes_per_country/ch-resilience_domain2pfx_routeviews.json", "switzerland"),\
                        ("../output/hardenize_parsed/prefixes_per_country/ee-tld_domain2pfx_routeviews.json", "estonia"),\
                        ("../output/hardenize_parsed/prefixes_per_country/lithuania-dashboard_domain2pfx_routeviews.json", "lithuania"),\
                        ("../output/hardenize_parsed/prefixes_per_country/sweden-health-status_domain2pfx_routeviews.json", "sweden"),\
                        ("../output/basisbeveiliging_parsed/domain2pfx_merged.json", "netherlands")]
    
    for tupl in domain2pfx_inputs:
        domain2pfx_input = tupl[0]
        domain2pfx_output = tupl[1]
        # Load domain-to-prefix mappings
        domain2pfx = read_json(domain2pfx_input)
        domain2visibility = {}

        # Calculate total prefixes to process for the progress bar
        total_prefixes = sum(len(prefixes) for prefixes in domain2pfx.values())

        # Process each prefix across all domains with a single progress bar
        with ThreadPoolExecutor(max_workers=10) as executor, tqdm(total=total_prefixes, desc="Processing Prefixes") as pbar:
            future_to_prefix = {
                executor.submit(process_visibility_for_prefix, prefix): (domain, prefix)
                for domain, prefixes in domain2pfx.items()
                for prefix in prefixes
            }

            # Collect results as they complete
            for future in as_completed(future_to_prefix):
                domain, prefix = future_to_prefix[future]
                average_visibility = future.result()

                # Update the result dictionary
                if domain not in domain2visibility:
                    domain2visibility[domain] = {}
                domain2visibility[domain][prefix] = average_visibility
                
                # Update progress bar
                pbar.update(1)

        # Save the final visibility data
        write_json("../output/characteristics/visibility/" + domain2pfx_output +  "_domain2visibility.json", domain2visibility)
