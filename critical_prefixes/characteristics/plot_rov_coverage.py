import ijson
import matplotlib.pyplot as plt
import numpy as np
from pprint import pprint
import matplotlib

# Function to read JSON incrementally using ijson
def read_json_stream(jsonfilename, key=None):
    def generator(f):
        if key:
            yield from ijson.items(f, f'{key}.item')
        else:
            yield from ijson.kvitems(f, '')

    with open(jsonfilename, 'r') as f:
        yield from generator(f)

if __name__ == "__main__":
    # Define multiple domain-to-ASN input sources
    domain2asn_inputs = [
        ("../output/basisbeveiliging_parsed/domain2asn.json", "netherlands"),
        # ("../output/hardenize_parsed/asns_per_country/bahamas-web-hygiene-dashboard_domain2asn.json", "bahamas"),
        ("../output/hardenize_parsed/asns_per_country/ch-resilience_domain2asn.json", "switzerland"),
        ("../output/hardenize_parsed/asns_per_country/ee-tld_domain2asn.json", "estonia"),
        ("../output/hardenize_parsed/asns_per_country/lithuania-dashboard_domain2asn.json", "lithuania"),
        ("../output/hardenize_parsed/asns_per_country/sweden-health-status_domain2asn.json", "sweden"),
    ]

    # Load ASNs per country
    country_asns = {country: set() for _, country in domain2asn_inputs}
    for filepath, country in domain2asn_inputs:
        for domain, asns in read_json_stream(filepath):
            country_asns[country].update(asns)

    # Load ROV scores incrementally & store only necessary data
    country_latest_ratios = {country: [] for country in country_asns}
    all_latest_ratios = []

    target_year_month = "2024-12"

    for asn, records in read_json_stream("../../rovista/rov_score_per_asn.json"):
        if not records or "error" in records:
            continue

        # Find latest record for the given month
        last_record = next((r for r in reversed(records) if r["asnDateKey"]["recordDate"].startswith(target_year_month)), None)

        if last_record:
            ratio = last_record["ratio"]
            all_latest_ratios.append(ratio)  # Global ROV compliance

            for country, asns in country_asns.items():
                if asn in asns:
                    country_latest_ratios[country].append(ratio)

    # Print stats
    print(f"Total ASNs with ROV scores: {len(all_latest_ratios)}")
    for country, ratios in country_latest_ratios.items():
        print(f"{country}: {len(ratios)} ratios")

    # Increase font size
    matplotlib.rc('font', size=15)

    # Create 2x3 subplots for CDFs with global ASNs comparison
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    all_latest_ratios = np.sort(all_latest_ratios)
    all_cdf = np.arange(1, len(all_latest_ratios) + 1) / len(all_latest_ratios)

    for idx, (country, ratios) in enumerate(country_latest_ratios.items()):
        if ratios:
            ratios = np.sort(ratios)
            cdf = np.arange(1, len(ratios) + 1) / len(ratios)
            axes[idx].plot(all_latest_ratios, all_cdf, marker=".", linestyle="--", color='grey', label="All ASNs")
            axes[idx].plot(ratios, cdf, marker=".", linestyle="-", color='black', label=country.capitalize())
            axes[idx].set_title(f"CDF of ROV Coverage Ratios ({country.capitalize()})")
            axes[idx].legend()
            axes[idx].grid()

    plt.tight_layout()
    plt.savefig("../output/characteristics/rov/rov_coverage_cdfs_comparison.png")

    # Create separate CDF for all ASNs from selected countries
    plt.figure(figsize=(10, 6))
    plt.plot(all_latest_ratios, all_cdf, marker=".", linestyle="-", color='grey', label="All ASNs")

    for country, ratios in country_latest_ratios.items():
        if ratios:
            ratios = np.sort(ratios)
            cdf = np.arange(1, len(ratios) + 1) / len(ratios)
            plt.plot(ratios, cdf, marker=".", linestyle="-", label=country.capitalize())

    plt.xlabel("ROV Coverage Ratio")
    plt.ylabel("CDF")
    plt.title("CDF of ROV Coverage Ratios (Selected Countries)")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig("../output/characteristics/rov/rov_coverage_cdfs_selected.png")

    # Adjust y-axis limit and plot the barplot properly
    plt.figure(figsize=(10, 6))
    bins = np.linspace(0, 1, 11)
    bin_width = np.diff(bins)[0] / len(country_latest_ratios)

    for idx, (country, ratios) in enumerate(country_latest_ratios.items()):
        if ratios:
            hist, _ = np.histogram(ratios, bins=bins)
            hist = hist / len(ratios)
            plt.bar(bins[:-1] + idx * bin_width + bin_width / 2, hist, width=bin_width, label=country.capitalize(), alpha=0.7)

    plt.xlabel("ROV Coverage Ratio")
    plt.ylabel("Proportion of ASNs")
    plt.xticks(np.linspace(0, 1, 11))  
    plt.ylim(0, 1)
    plt.title("Distribution of ROV Coverage Ratios")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig("../output/characteristics/rov/rov_coverage_barplot.png")
