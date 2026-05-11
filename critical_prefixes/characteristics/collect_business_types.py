import json
from pprint import pprint as pprint
import matplotlib.pyplot as plt
import glob
import os
import csv
from collections import defaultdict
import numpy as np
from collections import Counter

# Reads content from a json file
def read_json(jsonfilename):
    with open(jsonfilename, 'r') as jsonfile:
        return json.load(jsonfile)

# Reads content from a txt file
def read_txt(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file]

# Reads multiple JSON files and merges their contents
def read_multiple_json(files):
    merged_data = {}
    for file in files:
        with open(file, 'r') as f:
            data = json.load(f)
            merged_data.update(data)  # Merge dictionaries
    return merged_data

# Writes content to a JSON file
def write_json(jsonfilename, content):
    with open(jsonfilename, 'w') as fp:
        json.dump(content, fp, indent=4)

# CDF plot of business types
def business_type_cdfplot(filename, sorted_labels, sorted_frequencies):
    cdf = np.cumsum(sorted_frequencies) / sum(sorted_frequencies)
    plt.figure(figsize=(12, 6))
    plt.plot(sorted_labels, cdf, marker='.', linestyle='-', color='black')
    plt.xlabel("Business Types", fontsize=15)
    plt.ylabel("Cumulative Probability", fontsize=15)
    plt.ylim(-0.05, 1.05)
    plt.title("CDF of Business Types", fontsize=15)
    plt.xticks(rotation=90, ha="right", fontsize=10)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(filename)
    plt.clf()

def as2business_asdb(prefixes_per_origin, prefixes, as2type):
    dutch_origin_to_business = {}
    for prefix in prefixes:
        if prefix in prefixes_per_origin:
            origins = prefixes_per_origin[prefix]["origin"]
            for origin in origins:
                origin_asn = str(origin["asn"])
                if origin_asn not in dutch_origin_to_business:
                    dutch_origin_to_business[origin_asn] = as2type.get(origin_asn, ['Unknown'])
    return dutch_origin_to_business

def plot_business_labels_distribution(dutch_origin_to_business, data_source):
    flattened_list = [item for sublist in dutch_origin_to_business.values() for item in sublist]
    frequency = Counter(flattened_list)
    sorted_items = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
    sorted_labels, sorted_frequencies = zip(*sorted_items)

    max_label_length = 25 if data_source == "basisbeveiliging" else 16
    truncated_labels = [label[:max_label_length] + '...' if len(label) > max_label_length else label for label in sorted_labels]

    pprint(truncated_labels)
    plt.rcParams.update({'font.size': 15})
    
    plt.figure(figsize=(16, 10))
    plt.bar(truncated_labels, sorted_frequencies, color='black')
    plt.xticks(rotation=90, ha="right")
    plt.xlabel('Business Types')
    plt.ylabel('Frequency')
    plt.title('Frequency of Business Types')
    plt.tight_layout()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig(f"../output/characteristics/business_types/business_types_bar_{data_source}.png")
    plt.clf()
    
    business_type_cdfplot(f"../output/characteristics/business_types/business_types_cdf_{data_source}.png", truncated_labels, sorted_frequencies)

def count_ases_per_category(filename, dutch_origin_to_business):
    category_counts = Counter()
    for asn, categories in dutch_origin_to_business.items():
        for category in set(categories):  # Avoid duplicate counts within a single AS
            category_counts[category] += 1
    
    sorted_category_counts = dict(sorted(category_counts.items(), key=lambda x: x[1], reverse=True))

    # Print and save results
    write_json(filename, sorted_category_counts)

def plot_anycast_cdf(prefixes, anycast_census_v4_path, anycast_census_v6_path, bgp_tools_v4_path, bgp_tools_v6_path):
    # Set global font size for all plots
    plt.rcParams.update({'font.size': 15})
    # Load data from files
    anycast_census_v4 = [item['prefix'] for item in read_json(anycast_census_v4_path)]
    anycast_census_v6 = [item['prefix'] for item in read_json(anycast_census_v6_path)]
    bgp_tools_v4 = read_txt(bgp_tools_v4_path)
    bgp_tools_v6 = read_txt(bgp_tools_v6_path)

    # Merge the lists
    anycast_census_merged = anycast_census_v4 + anycast_census_v6
    bgp_tools_merged = bgp_tools_v4 + bgp_tools_v6

    # Initialize cumulative counts
    anycast_census_counts = np.cumsum([1 if prefix in anycast_census_merged else 0 for prefix in prefixes])
    bgp_tools_counts = np.cumsum([1 if prefix in bgp_tools_merged else 0 for prefix in prefixes])

    # Normalize counts to create CDFs
    total_prefixes = len(prefixes)
    cdf_anycast_census = anycast_census_counts / total_prefixes
    cdf_bgp_tools = bgp_tools_counts / total_prefixes

    # X-axis for plotting (as ratios)
    x_values = np.linspace(0, 1, total_prefixes)

    # Plot the CDFs
    plt.plot(cdf_anycast_census, x_values, label='Anycast Census', linestyle='-', marker='o', color = 'black')
    plt.plot(cdf_bgp_tools, x_values,  label='BGP Tools', linestyle='-', marker='x', color = 'grey')

    # Add plot labels and legend
    plt.title("CDF of Anycasted Prefixes Identified")
    plt.xlabel("Number of Prefixes")
    plt.ylabel("CDF of Anycasted Critical Prefixes")
    plt.legend(loc='lower right')
    plt.grid(True)
    plt.savefig("../output/characteristics/anycasting/prefix2anycast_cdf.png")
    plt.clf()  # Clear the current figure

    # Identify prefixes inferred by BGP Tools but not Anycast Census
    bgptools_only_prefixes = set(bgp_tools_merged) - set(anycast_census_merged)
    print("Prefixes inferred by BGP Tools but not by Anycast Census:")
    pprint(bgptools_only_prefixes)

    # Identify prefixes inferred by BGP Tools but not Anycast Census
    anycastcensus_only_prefixes = set(anycast_census_merged) - set(bgp_tools_merged)
    print("Prefixes inferred by Anycast Census but not by BGP Tools:")
    pprint(anycastcensus_only_prefixes)

    print("Ratio of anycast prefixes announced by bgp.tools and anycast.census")
    pprint(cdf_bgp_tools[-1])
    pprint(cdf_anycast_census[-1])



if __name__ == '__main__':
    plt.rcParams.update({'font.size': 15})

    # Extra input files for ASNs
    asn_files = [
        "../output/basisbeveiliging_parsed/domain2asn.json",
        # "../output/hardenize_parsed/asns_per_country/bahamas-web-hygiene-dashboard_domain2asn.json",
        "../output/hardenize_parsed/asns_per_country/ch-resilience_domain2asn.json",
        "../output/hardenize_parsed/asns_per_country/ee-tld_domain2asn.json",
        "../output/hardenize_parsed/asns_per_country/lithuania-dashboard_domain2asn.json",
        "../output/hardenize_parsed/asns_per_country/sweden-health-status_domain2asn.json"
    ]
    
    # Extra input files for prefixes per origin
    prefix_files = [
        # "../output/characteristics/rpki/prefix2origin_bahamas.json",
        "../output/characteristics/rpki/prefix2origin_netherlands.json",
        "../output/characteristics/rpki/prefix2origin_estonia.json",
        "../output/characteristics/rpki/prefix2origin_lithuania.json",
        "../output/characteristics/rpki/prefix2origin_sweden.json",
        "../output/characteristics/rpki/prefix2origin_switzerland.json"
    ]

    # Load and merge data
    asn_per_domain = read_multiple_json(asn_files)
    prefixes_per_origin = read_multiple_json(prefix_files)
    
    # Extract all prefixes
    prefixes = list(prefixes_per_origin.keys())

    # Process AS business types per ASdb
    as2type = read_multiple_json(["../../asdb/2024-01_categorized_ases.json"])
    dutch_origin_to_business_asdb = as2business_asdb(prefixes_per_origin, prefixes, as2type)

    # Plot business labels distribution for ASdb
    count_ases_per_category("../output/characteristics/business_types/asdb_business_type_counts.json", dutch_origin_to_business_asdb)
    plot_business_labels_distribution(dutch_origin_to_business_asdb, "asdb")

    plot_anycast_cdf(
        prefixes,
        "../../anycast-census/11/2024-11-01_v4.json",
        "../../anycast-census/11/2024-11-01_v6.json",
        "../../bgptools/anycatch-v4-prefixes.txt",
        "../../bgptools/anycatch-v6-prefixes.txt"
    )

