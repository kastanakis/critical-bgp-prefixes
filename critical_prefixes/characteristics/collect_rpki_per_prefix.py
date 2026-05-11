import json
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Writes content to a JSON file
def write_json(jsonfilename, content):
    with open(jsonfilename, 'w') as fp:
        json.dump(content, fp, indent=4)

# Reads content of JSON file and returns it
def read_json(jsonfilename):
    with open(jsonfilename, 'r') as jsonfile:
        return json.load(jsonfile)

def fetch_prefix_status(resource):
    """
    Fetch prefix-status data from the RIPE API for a given resource.
    """
    url = "https://stat.ripe.net/data/prefix-overview/data.json"
    params = {'data_overload_limit': 'ignore', 'resource': resource}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from RIPE API for {resource}: {e}")
        return None

def fetch_rpki_data(asn, prefix):
    """
    Fetch RPKI validation data from the RIPE API for a given resource.
    """
    url = "https://stat.ripe.net/data/rpki-validation/data.json"
    params = {"resource": asn, "prefix": prefix}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from RIPE API for {asn}: {e}")
        return None

def process_prefix_origin(prefix):
    """
    Retrieves ASN origin data for a given prefix.
    """
    pref_stat = fetch_prefix_status(prefix)
    if pref_stat and 'data' in pref_stat and 'asns' in pref_stat['data']:
        holders = pref_stat['data']['asns']
        related = pref_stat['data']['related_prefixes']
        return {'origin': holders, 'related_prefixes': related}
    return None

def process_prefix_rpki(asn, prefix):
    """
    Retrieves RPKI validation status for a given ASN and prefix.
    """
    rpki_stat = fetch_rpki_data(asn, prefix)
    if rpki_stat and 'data' in rpki_stat:
        return rpki_stat['data']
    return None

if __name__ == '__main__':
    # Define country-specific prefix input files
    domain2pfx_inputs = [
        ("../output/hardenize_parsed/prefixes_per_country/bahamas-web-hygiene-dashboard_domain2pfx_routeviews.json", "bahamas"),
        ("../output/hardenize_parsed/prefixes_per_country/ch-resilience_domain2pfx_routeviews.json", "switzerland"),
        ("../output/hardenize_parsed/prefixes_per_country/ee-tld_domain2pfx_routeviews.json", "estonia"),
        ("../output/hardenize_parsed/prefixes_per_country/lithuania-dashboard_domain2pfx_routeviews.json", "lithuania"),
        ("../output/hardenize_parsed/prefixes_per_country/sweden-health-status_domain2pfx_routeviews.json", "sweden"),
        ("../output/basisbeveiliging_parsed/domain2pfx_merged.json", "netherlands")
    ]

    # Process each country separately
    for filepath, country in domain2pfx_inputs:
        print(f"\nProcessing {country.upper()}...\n")

        # Load country-specific prefixes
        domain2pfx = read_json(filepath)
        prefixes = list({prefix for values_list in domain2pfx.values() for prefix in values_list})

        # Step 1: Get ASN origins
        origin_results = {}
        with ThreadPoolExecutor(max_workers=10) as executor, tqdm(total=len(prefixes), desc=f"Processing {country} Prefixes") as pbar:
            futures = {executor.submit(process_prefix_origin, prefix): prefix for prefix in prefixes}
            for future in as_completed(futures):
                pref = futures[future]
                try:
                    result = future.result()
                    if result:
                        origin_results[pref] = result
                except Exception as e:
                    print(f"Error processing prefix {pref}: {e}")
                pbar.update(1)

        # Save origin results
        write_json(f"../output/characteristics/rpki/prefix2origin_{country}.json", origin_results)

        # Step 2: Get RPKI validation data
        rpki_results = {}
        with ThreadPoolExecutor(max_workers=10) as executor, tqdm(total=len(origin_results), desc=f"Processing {country} RPKI") as pbar:
            futures = {
                executor.submit(process_prefix_rpki, origin["asn"], prefix): (origin["asn"], prefix)
                for prefix in origin_results
                for origin in origin_results[prefix]['origin']
            }
            for future in as_completed(futures):
                asn, prefix = futures[future]
                try:
                    res = future.result()
                    rpki_results[prefix] = res
                except Exception as e:
                    print(f"Error processing prefix {prefix} with ASN {asn}: {e}")
                pbar.update(1)

        # Save RPKI results
        write_json(f"../output/characteristics/rpki/prefix2rpki_{country}.json", rpki_results)

    print("\n✅ Processing complete for all countries!\n")
