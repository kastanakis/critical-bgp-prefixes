import json
import csv
from tqdm import tqdm
import requests
from pprint import pprint as pprint
from concurrent.futures import ThreadPoolExecutor, as_completed

# Reads content from a JSON file
def read_json(jsonfilename):
    with open(jsonfilename, 'r') as jsonfile:
        return json.load(jsonfile)

# Writes content to a JSON file
def write_json(jsonfilename, content):
    with open(jsonfilename, 'w') as fp:
        json.dump(content, fp, indent=4)

def get_public_asns(as2rel_url):
    as2rel_dict = dict()
    public_asns = set()

    # Unbox the as2rel dataset
    with open(as2rel_url, 'r') as csvfile:
        csvreader = csv.reader(csvfile, delimiter='|')
        for row in csvreader:
            if row[0][0] != '#':  # ignore lines starting with "#"
                as1 = int(row[0])
                as2 = int(row[1])
                rel = int(row[2])

                if as1 not in as2rel_dict:
                    as2rel_dict[as1] = list()
                as2rel_dict[as1].append([as2, rel])

                if as2 not in as2rel_dict:
                    as2rel_dict[as2] = list()
                as2rel_dict[as2].append([as1, -rel])

                # Add as1 and as2 in the public asns set
                public_asns.add(as1)
                public_asns.add(as2)
    public_asns_list = list(public_asns)
    return public_asns_list

def fetch_rovista_data(asn):
    """
    Fetch routing data for a single prefix using RIPE API.
    """
    url = f"https://api.rovista.netsecurelab.org/rovista/api/AS-rov-scores/{asn}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return asn, response.json()
        else:
            return asn, []
    except requests.exceptions.RequestException as e:
        return asn, {"error": str(e)}
    
if __name__ == "__main__":
    all_asns = get_public_asns("../caida/20250101.as-rel2.txt")
    rovista_coverage = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(fetch_rovista_data, asn): asn for asn in all_asns
        }
        with tqdm(total=len(all_asns), desc="Processing ASes", unit="AS") as pbar:
            for future in as_completed(futures):
                asn, result = future.result()
                rovista_coverage[asn] = result
                pbar.update(1)
    executor.shutdown(wait=True)
    write_json("rov_score_per_asn.json", rovista_coverage)