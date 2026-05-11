import requests
import json
import datetime
import numpy as np
import matplotlib.pyplot as plt
import os
import csv
from pprint import pprint
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import random

# Writes content to a JSON file
def write_json(jsonfilename, content):
    with open(jsonfilename, 'w') as fp:
        json.dump(content, fp, indent=4)

def get_public_asns(as2rel_url):
    """
    Reads a CAIDA as-rel file and returns a list of all unique public ASNs.
    """
    as2rel_dict = dict()
    public_asns = set()

    with open(as2rel_url, 'r') as csvfile:
        csvreader = csv.reader(csvfile, delimiter='|')
        for row in csvreader:
            if not row or row[0].startswith('#'):
                continue  # skip comment or empty lines
            as1 = int(row[0])
            as2 = int(row[1])
            rel = int(row[2])

            if as1 not in as2rel_dict:
                as2rel_dict[as1] = []
            as2rel_dict[as1].append([as2, rel])

            if as2 not in as2rel_dict:
                as2rel_dict[as2] = []
            as2rel_dict[as2].append([as1, -rel])

            public_asns.add(as1)
            public_asns.add(as2)

    return list(public_asns)

def get_unique_asns(file_path):
    """
    Returns a list of unique ASNs from a JSON file mapping domains to ASNs.
    {
       "domain1.com": [asn1, asn2, ...],
       "domain2.com": [asn3, asn4],
       ...
    }
    """
    with open(file_path, 'r') as file:
        data = json.load(file)
    total_asns = [asn for asn_list in data.values() for asn in asn_list]
    return list(set(total_asns))

def fetch_outage_data(asn, start_time, end_time):
    """
    Fetch outage data for a single ASN from the IODA API
    and return (asn, [ { 'total_down_times': ... }, [ {start, duration}, ... ] ]).
    """
    api_url = (
        "https://api.ioda.inetintel.cc.gatech.edu/v2/outages/events?"
        f"entityType=asn&entityCode={asn}&from={start_time}&until={end_time}"
    )
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            json_response = response.json()
            data = json_response.get('data', [])

            down_time_counter = len(data)
            down_time_details = []
            if down_time_counter > 0:
                for outage in data:
                    start_val = outage.get("start")
                    duration_val = outage.get("duration")
                    down_time_details.append({"start": start_val, "duration": duration_val})

            return asn, [
                {"total_down_times": down_time_counter},
                down_time_details
            ]
        else:
            # Non-200 response => default to zero
            return asn, [
                {"total_down_times": 0},
                []
            ]
    except Exception:
        # On exception, default to zero
        return asn, [
            {"total_down_times": 0},
            []
        ]

def main():
    # Increase the global font size for titles, labels, and ticks
    plt.rcParams.update({'font.size': 15})

    # 1) Load the full CAIDA dataset and pick xx random ASNs
    all_asns = get_public_asns("../../caida/20250101.as-rel2.txt")
    random_asns = random.sample(all_asns, 10000)

    # 2) Fetch the outage data for the random ASNs (so we can plot them later)
    print(f"Fetching outage data for xx random ASNs...")
    start_time = "1730415600"  # Nov 01 2024 00:00:00 UTC
    end_time   = "1733007599"  # Nov 30 2024 23:59:59 UTC

    random_down_time_asn = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for asn in random_asns:
            futures.append(executor.submit(fetch_outage_data, asn, start_time, end_time))

        for future in tqdm(as_completed(futures),
                           total=len(futures),
                           desc="Processing all ASNs",
                           unit="ASN"):
            asn, result = future.result()
            random_down_time_asn[asn] = result

    # Convert the random ASNs’ downtime data into a CDF
    random_downtime_counts = [val[0]["total_down_times"] for val in random_down_time_asn.values()]
    random_downtime_counts = np.sort(random_downtime_counts)
    n_rand = len(random_downtime_counts)
    random_cdf_vals = np.arange(1, n_rand + 1) / n_rand

    # 3) Prepare domain-to-ASN input sources
    domain2asn_inputs = [
        ("../output/basisbeveiliging_parsed/domain2asn.json", "netherlands"),
        ("../output/hardenize_parsed/asns_per_country/bahamas-web-hygiene-dashboard_domain2asn.json", "bahamas"),
        ("../output/hardenize_parsed/asns_per_country/ch-resilience_domain2asn.json", "switzerland"),
        ("../output/hardenize_parsed/asns_per_country/ee-tld_domain2asn.json", "estonia"),
        ("../output/hardenize_parsed/asns_per_country/lithuania-dashboard_domain2asn.json", "lithuania"),
        ("../output/hardenize_parsed/asns_per_country/sweden-health-status_domain2asn.json", "sweden"),
    ]

    # Time range in human-readable form for logging
    start_time_date = datetime.datetime.fromtimestamp(int(start_time), datetime.timezone.utc)
    end_time_date = datetime.datetime.fromtimestamp(int(end_time), datetime.timezone.utc)
    print(f"Querying outages from {start_time_date} to {end_time_date} (UTC)")

    # 4) One unified JSON file for all countries
    out_dir = "../output/characteristics/outages"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    unified_json_path = os.path.join(out_dir, "down_time_per_asn_unified.json")

    # 5) Collect outages in all_outages dict
    all_outages = {}
    if os.path.exists(unified_json_path):
        # If the unified JSON already exists, skip IODA fetch for countries
        print(f"Unified JSON exists -> {unified_json_path}. Loading data from file, skipping download.")
        with open(unified_json_path, 'r') as f:
            all_outages = json.load(f)
    else:
        print("No unified JSON found. Fetching data from IODA for each country...")
        for file_path, country_label in domain2asn_inputs:
            print(f"\n=== Processing: {file_path} for label: {country_label} ===")

            unique_asns = get_unique_asns(file_path)
            print(f"Found {len(unique_asns)} unique ASNs for {country_label}")

            down_time_asn = {}
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                for asn in unique_asns:
                    futures.append(executor.submit(fetch_outage_data, asn, start_time, end_time))

                # Show progress bar
                for future in tqdm(as_completed(futures),
                                   total=len(futures),
                                   desc=f"Processing ASNs for {country_label}",
                                   unit="ASN"):
                    asn, result = future.result()
                    down_time_asn[asn] = result

            all_outages[country_label] = down_time_asn

        # Write out the unified JSON for all countries
        write_json(unified_json_path, all_outages)
        print(f"Wrote unified downtime data to {unified_json_path}")

    # # 6) Create 2x3 subplots for the countries + compare with the random ASNs
    # num_countries = len(domain2asn_inputs)  # expecting 6
    # nrows, ncols = 2, 3
    # fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(15, 8))

    # all_downtime_counts = []  # For a unified "all countries" CDF

    # for idx, (file_path, country_label) in enumerate(domain2asn_inputs):
    #     country_outages = all_outages.get(country_label, {})
    #     # Extract total_down_times
    #     downtime_counts = [val[0]["total_down_times"] for val in country_outages.values()]
    #     if not downtime_counts:
    #         continue

    #     # Add to the unified "all countries" distribution
    #     all_downtime_counts.extend(downtime_counts)

    #     # Sort and compute the empirical CDF
    #     sorted_counts = np.sort(downtime_counts)
    #     n = len(sorted_counts)
    #     cdf_vals = np.arange(1, n + 1) / n

    #     ax = axes[idx // ncols, idx % ncols]
    #     # Plot the country's distribution in black
    #     ax.plot(sorted_counts, cdf_vals, marker='.', linestyle='-', color='k', label=f"{country_label.capitalize()}")
    #     # Plot the random ASNs distribution in red dashed
    #     ax.plot(random_downtime_counts, random_cdf_vals, marker='.', linestyle='--', color='r', label="All ASNs")

    #     ax.set_xlabel("Total Downtimes (Nov 2024)")
    #     ax.set_ylabel("CDF")
    #     ax.set_title(country_label.capitalize())
    #     ax.grid(True)
    #     ax.legend()

    # plt.tight_layout()
    # subplot_png = os.path.join(out_dir, "all_countries_downtime_cdf_subplots.png")
    # plt.savefig(subplot_png, dpi=300)
    # print(f"CDF subplots saved successfully at {subplot_png}!")

    # # 7) Create a unified CDF across all countries + compare with random
    # if all_downtime_counts:
    #     all_downtime_counts = np.sort(all_downtime_counts)
    #     n_all = len(all_downtime_counts)
    #     all_cdf_vals = np.arange(1, n_all + 1) / n_all

    #     plt.figure(figsize=(8, 6))
    #     # Plot the combined distribution of all countries
    #     plt.plot(all_downtime_counts, all_cdf_vals, marker='.', linestyle='-', color='k', label="All Countries")
    #     # Plot the random ASNs distribution
    #     plt.plot(random_downtime_counts, random_cdf_vals, marker='.', linestyle='--', color='r', label="Random ASNs")
    #     plt.xlabel("Total Downtimes (Nov 2024)", fontsize=15)
    #     plt.ylabel("CDF", fontsize=15)
    #     plt.title("All Countries vs Random Sample", fontsize=15)
    #     plt.grid(True)
    #     plt.legend()

    #     unified_png = os.path.join(out_dir, "unified_downtime_cdf.png")
    #     plt.savefig(unified_png, dpi=300)
    #     print(f"Unified CDF saved successfully at {unified_png}!")
    # else:
    #     print("No downtime data was collected from the country datasets, so no unified CDF can be generated.")

if __name__ == '__main__':
    main()
