import json
import os
import glob
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
from pprint import pprint as pprint

def grouped_barplot_one_fig(filename, country_data, xlabel, ylabel, title):
    """
    Creates a grouped bar plot where each country is represented with a distinct color.
    """
    plt.figure(figsize=(12, 6))
    width = 0.15  # Bar width
    colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown']  # Assign colors per country
    
    all_values = set()
    for data in country_data.values():
        all_values.update(data)
    all_values = sorted(all_values)
    
    x_indices = np.arange(len(all_values))
    
    for i, (country, data) in enumerate(country_data.items()):
        counts = Counter(data)
        frequencies = [counts.get(val, 0) for val in all_values]
        
        # Normalize to proportions
        total = sum(frequencies)
        proportions = [f / total if total > 0 else 0 for f in frequencies]
        
        plt.bar(x_indices + i * width, proportions, width=width, label=country.capitalize(), alpha=0.7)
    
    plt.title(title)
    plt.xticks(x_indices + (width * len(country_data) / 2), all_values)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(filename)
    plt.clf()

def grouped_barplot(ax, country_data, xlabel, ylabel, title, country_order, colors):
    """
    Creates a grouped bar plot where each country is represented with a distinct color.
    """
    width = 0.15  # Bar width
    
    all_values = set()
    for country in country_order:
        if country in country_data:
            all_values.update(country_data[country])
    all_values = sorted(all_values)
    
    x_indices = np.arange(len(all_values))
    
    for i, country in enumerate(country_order):
        if country in country_data:
            counts = Counter(country_data[country])
            frequencies = [counts.get(val, 0) for val in all_values]
            
            # Normalize to proportions
            total = sum(frequencies)
            proportions = [f / total if total > 0 else 0 for f in frequencies]
            
            ax.bar(x_indices + i * width, proportions, width=width, label=country, color=colors[i], alpha=0.7)
    
    ax.set_title(title)
    ax.set_xticks(x_indices + (width * len(country_data) / 2))
    ax.set_xticklabels(all_values, rotation=45)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)

def plot_combined_v4_v6(v4_data, v6_data, filename, country_order, colors):
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    grouped_barplot(axes[0], v4_data, "Prefix Length", "Proportion of ASNs", "IPv4 Prefix Lengths", country_order, colors)
    grouped_barplot(axes[1], v6_data, "Prefix Length", "Proportion of ASNs", "IPv6 Prefix Lengths", country_order, colors)
    plt.tight_layout()
    plt.savefig(filename)
    plt.clf()

if __name__ == '__main__':
    plt.rcParams.update({'font.size': 15})
    country_order = ["Netherlands", "Bahamas", "Switzerland", "Estonia", "Lithuania", "Sweden"]
    colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown']  # Fixed color order
    
    domain2asn_inputs = [
        ("../output/basisbeveiliging_parsed/domain2asn.json", "Netherlands"),
        ("../output/hardenize_parsed/asns_per_country/bahamas-web-hygiene-dashboard_domain2asn.json", "Bahamas"),
        ("../output/hardenize_parsed/asns_per_country/ch-resilience_domain2asn.json", "Switzerland"),
        ("../output/hardenize_parsed/asns_per_country/ee-tld_domain2asn.json", "Estonia"),
        ("../output/hardenize_parsed/asns_per_country/lithuania-dashboard_domain2asn.json", "Lithuania"),
        ("../output/hardenize_parsed/asns_per_country/sweden-health-status_domain2asn.json", "Sweden"),
    ]
    
    country_masks_v4 = {country: [] for country in country_order}
    country_masks_v6 = {country: [] for country in country_order}
    
    for file_path, country in domain2asn_inputs:
        prefixes_per_origin = json.load(open("../output/characteristics/rpki/prefix2origin_" + country.lower() + ".json"))
        prefixes = list(prefixes_per_origin.keys())
        
        masks_v4, masks_v6 = [], []
        for prefix in prefixes:
            mask = int(prefix.split('/')[1])
            (masks_v6 if ':' in prefix else masks_v4).append(mask)
        
        country_masks_v4[country] = masks_v4
        country_masks_v6[country] = masks_v6
    
    plot_combined_v4_v6(country_masks_v4, country_masks_v6, "../output/characteristics/administration/all_countries_v4_v6_prefix_length_distribution.png", country_order, colors)
    
    paths_per_prefix = json.load(open("../../ripestat/output/ribs/sanitized_paths_per_prefix_per_country.json"))
    country_path_lengths = {}
    country_order = ["netherlands", "bahamas", "switzerland", "estonia", "lithuania", "sweden"]
    for country in country_order:
        if country in paths_per_prefix:
            unique_paths = set()
            for prefix in paths_per_prefix[country]:
                for rc in paths_per_prefix[country][prefix]:
                    for path in paths_per_prefix[country][prefix][rc]:
                        unique_paths.add(tuple(path.split()))
            
            unique_path_lengths = [len(t) for t in unique_paths]
            country_path_lengths[country] = unique_path_lengths

    grouped_barplot_one_fig("../output/characteristics/administration/all_countries_path_lengths.png", country_path_lengths, "Path Length", "Proportion of Paths", "Distribution of AS Path Lengths")
