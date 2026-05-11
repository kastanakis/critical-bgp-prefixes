import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm  # Import tqdm for progress bars
import itertools

# Writes content to a JSON file
def write_json(jsonfilename, content):
    with open(jsonfilename, 'w') as fp:
        json.dump(content, fp, indent=4)

# Reads content of JSON file and returns
def read_json(jsonfilename):
    with open(jsonfilename, 'r') as jsonfile:
        return json.load(jsonfile)

def geolocate(prefix):
    """
    Fetch visibility data from the RIPE API for a given resource.
    """
    url = "https://stat-ui.stat.ripe.net/data/maxmind-geo-lite/data.json"
    params = {
        "data_overload_limit": "ignore",
        "resource": prefix
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from RIPE API for {prefix}: {e}")
        return None

def process_location_for_prefix(prefix):
    """
    Process visibility data for a single prefix and calculate average visibility.
    """
    location_data = geolocate(prefix)
    per_country_iso_codes = set()
    
    if location_data and 'data' in location_data and 'located_resources' in location_data['data']:
        located_resources = location_data['data']['located_resources']
        for located_resource in located_resources:
            if "locations" in located_resource:
                for location in located_resource["locations"]:
                    per_country_iso_codes.add(location['country'])
    return list(per_country_iso_codes)

# Returns a flat list from a list of lists
def flatten_list(lista):
    return list(itertools.chain.from_iterable(lista))

if __name__ == "__main__":
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
        prefixes = set(list(itertools.chain.from_iterable(read_json(domain2pfx_input).values())))
        
        prefix2loc = {}

        # Calculate total prefixes to process for the progress bar
        print(len(prefixes))
        
        # Process each prefix across all domains with a single progress bar
        with ThreadPoolExecutor(max_workers=10) as executor, tqdm(total=len(prefixes), desc="Processing Prefixes") as pbar:
            future_to_prefix = {
                executor.submit(process_location_for_prefix, prefix): prefix
                for prefix in prefixes
            }

            # Collect results as they complete
            for future in as_completed(future_to_prefix):
                prefix = future_to_prefix[future]
                locations_per_prefix = future.result()

                # Update the result dictionary
                prefix2loc[prefix] = locations_per_prefix
                
                # Update progress bar
                pbar.update(1)

        # Save the final visibility data
        write_json("../output/characteristics/geolocation/" + domain2pfx_output + "_prefix2location.json", prefix2loc)