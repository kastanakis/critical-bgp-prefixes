import json
import csv
import os
import matplotlib.pyplot as plt
import numpy as np

FONT_SIZE = 14  # Define a constant for font size

# Writes content to a JSON file
def write_json(jsonfilename, content):
    with open(jsonfilename, 'w') as fp:
        json.dump(content, fp, indent=4)

# Reads content of JSON file and returns
def read_json(jsonfilename):
    with open(jsonfilename, 'r') as jsonfile:
        return json.load(jsonfile)

# Extract providers from as2rel dataset
def find_as_providers(as2rel_url):
    providers = dict()
    with open(as2rel_url, 'r') as csvfile:
        csvreader = csv.reader(csvfile, delimiter='|')
        for row in csvreader:
            if row[0][0] != '#':  # Ignore commented lines
                as1 = str(row[0])
                as2 = str(row[1])
                rel = int(row[2])

                if rel == -1:  # If as1 is a provider of as2
                    if as2 not in providers:
                        providers[as2] = []
                    if as1 not in providers[as2]:
                        providers[as2].append(as1)
    return providers

# Plot CDFs for all countries as subplots
def plot_cdfs_subplots(output_path, country_data, all_data):
    countries = list(country_data.keys())
    fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(15, 10))

    for i, country in enumerate(countries):
        ax = axes[i // 3, i % 3]  # Calculate subplot position

        # Extract data
        sorted_data = np.sort(country_data[country])
        y_vals = np.arange(1, len(sorted_data) + 1) / len(sorted_data)

        # Extract reference global AS data
        sorted_all = np.sort(all_data)
        y_vals_all = np.arange(1, len(sorted_all) + 1) / len(sorted_all)

        # Plot CDF
        ax.plot(sorted_all, y_vals_all, marker='.', linestyle='-', color='grey', alpha=0.5, label="All ASes")
        ax.plot(sorted_data, y_vals, marker='.', linestyle='-', color='black', label=country.capitalize())

        # Customize subplot
        ax.set_xlabel("Number of Providers", fontsize=FONT_SIZE)
        ax.set_ylabel("CDF", fontsize=FONT_SIZE)
        ax.set_title(f"Resilience CDF - {country.capitalize()}", fontsize=FONT_SIZE)
        ax.set_xlim(0, 30)  # Set x-axis limit to 30
        ax.set_xticks(np.arange(0, 31, 2))  # Ensure ticks are consistent
        ax.grid(True)
        ax.legend(fontsize=FONT_SIZE)

    plt.tight_layout()
    
    # Save the combined figure
    save_path = os.path.join(output_path, "resilience_cdfs_all_countries_subplots.png")
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Saved: {save_path}")

# Plot a combined CDF for all countries together vs. global AS resilience
def plot_combined_cdf(output_path, all_countries_data, all_data):
    plt.figure(figsize=(8, 5))

    # Global AS resilience (grey)
    sorted_all = np.sort(all_data)
    y_vals_all = np.arange(1, len(sorted_all) + 1) / len(sorted_all)
    plt.plot(sorted_all, y_vals_all, marker='.', linestyle='-', color='grey', alpha=0.5, label="All ASes")

    # Combined country data (black)
    sorted_combined = np.sort(all_countries_data)
    y_vals_combined = np.arange(1, len(sorted_combined) + 1) / len(sorted_combined)
    plt.plot(sorted_combined, y_vals_combined, marker='.', linestyle='-', color='black', label="All Countries Combined")

    # Customize the plot
    plt.xlabel("Number of Providers", fontsize=FONT_SIZE)
    plt.ylabel("CDF", fontsize=FONT_SIZE)
    plt.title("All ASes vs. Critical ASes", fontsize=FONT_SIZE)
    plt.xlim(0, 30)
    plt.xticks(np.arange(0, 31, 2), fontsize=FONT_SIZE)
    plt.yticks(fontsize=FONT_SIZE)
    plt.grid(True)
    plt.legend(fontsize=FONT_SIZE)
    plt.tight_layout()

    # Save the plot
    save_path = os.path.join(output_path, "resilience_cdf_all_countries.png")
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Saved: {save_path}")

if __name__ == "__main__":
    # Load AS-to-provider mapping
    as_providers = find_as_providers("../../caida/20241101.as-rel2.txt")
    count = sum(1 for values in as_providers.values() if len(values) > 1)
    print("{} out of {} ASes are multihomed".format(count, len(as_providers.keys())))

    # Extract provider counts for all ASes
    all_provider_counts = [len(providers) for providers in as_providers.values()]

    # Load domain-to-ASN mapping for multiple countries
    domain2asn_inputs = [
        ("../output/basisbeveiliging_parsed/domain2asn.json", "netherlands"),
        # ("../output/hardenize_parsed/asns_per_country/bahamas-web-hygiene-dashboard_domain2asn.json", "bahamas"),
        ("../output/hardenize_parsed/asns_per_country/ch-resilience_domain2asn.json", "switzerland"),
        ("../output/hardenize_parsed/asns_per_country/ee-tld_domain2asn.json", "estonia"),
        ("../output/hardenize_parsed/asns_per_country/lithuania-dashboard_domain2asn.json", "lithuania"),
        ("../output/hardenize_parsed/asns_per_country/sweden-health-status_domain2asn.json", "sweden"),
    ]

    country_provider_counts = {}
    output_dir = "../output/characteristics/resilience/"

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    all_countries_combined = []

    for filepath, country in domain2asn_inputs:
        domain2asn = read_json(filepath)
        provider_counts = {}

        for domain, asns in domain2asn.items():
            for asn in asns:
                if asn in as_providers:
                    if len(as_providers[asn]) > 1: 
                        provider_counts[domain] = len(as_providers[asn]) 
                        break
        
        country_provider_counts[country] = list(provider_counts.values())
        all_countries_combined.extend(provider_counts.values())

        # Save per-country domain-to-resilience data
        resilience_file = os.path.join(output_dir, f"domain2resilience_{country}.json")
        write_json(resilience_file, provider_counts)

    # Save provider count data for all countries
    write_json(os.path.join(output_dir, "country_provider_counts.json"), country_provider_counts)

    # Generate subplot CDFs for all countries
    plot_cdfs_subplots(output_dir, country_provider_counts, all_provider_counts)

    # Generate the combined CDF plot
    plot_combined_cdf(output_dir, all_countries_combined, all_provider_counts)
