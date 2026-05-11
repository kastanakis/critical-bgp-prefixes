import csv
import json
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

def read_csv(filename):
    pop_dict = {}
    with open(filename, 'r') as csvfile_in:
        tranco_in = csv.reader(csvfile_in, delimiter=',')
        for line in tranco_in:
            pop_dict[line[1]] = int(line[0])
    return pop_dict

def write_json(jsonfilename, content):
    with open(jsonfilename, 'w') as fp:
        json.dump(content, fp, indent=4)

def read_json(jsonfilename):
    with open(jsonfilename, 'r') as jsonfile:
        return json.load(jsonfile)

def plot_heatmap(data, title, output_file):
    n = len(data)
    num_columns = math.ceil(math.sqrt(n))
    num_rows = math.ceil(n / num_columns)
    padded_values = data + [-2] * (num_rows * num_columns - n)
    heatmap_array = np.array(padded_values).reshape(num_rows, num_columns)

    fig, ax = plt.subplots(figsize=(12, 8))

    cmap_grayscale = plt.cm.Greys
    norm = plt.Normalize(vmin=0, vmax=max(data))

    for i in range(num_rows):
        for j in range(num_columns):
            value = heatmap_array[i, j]
            if value == -2:
                ax.add_patch(
                    plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, hatch='///', edgecolor='gray')
                )
            elif value == -1:
                ax.add_patch(
                    plt.Rectangle((j - 0.5, i - 0.5), 1, 1, color='red')
                )
            else:
                ax.add_patch(
                    plt.Rectangle((j - 0.5, i - 0.5), 1, 1, color=cmap_grayscale(norm(value)))
                )

    ax.set_xlim(-0.5, num_columns - 0.5)
    ax.set_ylim(-0.5, num_rows - 0.5)
    ax.set_aspect('equal')
    ax.set_xticks(np.arange(-0.5, heatmap_array.shape[1], 1), minor=True)
    ax.set_yticks(np.arange(-0.5, heatmap_array.shape[0], 1), minor=True)
    ax.grid(which='minor', color='black', linestyle='--', linewidth=0.5, alpha=0.5)
    ax.tick_params(which="minor", size=0)
    ax.invert_yaxis()

    sm = plt.cm.ScalarMappable(cmap=cmap_grayscale, norm=norm)
    sm.set_array([])

    cbar = fig.colorbar(sm, ax=ax, label='Popularity Scale')
    cbar.set_ticks([-1, max(data)/2, max(data)])
    cbar.set_ticklabels(['No Popularity (-1)', 'Low Popularity', 'High Popularity'])

    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

if __name__ == '__main__':
    plt.rcParams.update({'font.size': 17})

    domain2pfx_inputs = [("../output/hardenize_parsed/prefixes_per_country/bahamas-web-hygiene-dashboard_domain2pfx_routeviews.json", "bahamas"),\
                        ("../output/hardenize_parsed/prefixes_per_country/ch-resilience_domain2pfx_routeviews.json", "switzerland"),\
                        ("../output/hardenize_parsed/prefixes_per_country/ee-tld_domain2pfx_routeviews.json", "estonia"),\
                        ("../output/hardenize_parsed/prefixes_per_country/lithuania-dashboard_domain2pfx_routeviews.json", "lithuania"),\
                        ("../output/hardenize_parsed/prefixes_per_country/sweden-health-status_domain2pfx_routeviews.json", "sweden"),\
                        ("../output/basisbeveiliging_parsed/domain2pfx_merged.json", "netherlands")]

    tranco_prefixes = read_json("../output/tranco_parsed/domain2pfx_routeviews.json")
    tranco_original = read_csv("../../tranco/top-1m_november_2024.csv")

    summary_data = []
    
    for input_file, country_name in domain2pfx_inputs:
        basisb_prefixes = read_json(input_file)

        prefix_to_index = {}
        for tranco_domain, prefixes in tranco_prefixes.items():
            if tranco_domain in tranco_original:
                index = tranco_original[tranco_domain]
                for prefix in prefixes:
                    if prefix not in prefix_to_index:
                        prefix_to_index[prefix] = set()
                    prefix_to_index[prefix].add(index)

        prefix_to_index = {key: list(value) for key, value in prefix_to_index.items()}
        write_json(f'../output/characteristics/popularity/{country_name}_prefix2popularity.json', prefix_to_index)

        min_values = {prefix: min(values) for prefix, values in prefix_to_index.items()}

        popularity_per_prefix = {}
        for prefixes in basisb_prefixes.values():
            for prefix in prefixes:
                if prefix in min_values:
                    popularity_per_prefix[prefix] = min_values[prefix]
                else:
                    popularity_per_prefix[prefix] = -1

        write_json(f'../output/characteristics/popularity/{country_name}_prefix2popularity.json', popularity_per_prefix)

        popularity_per_domain = {}
        for domain in basisb_prefixes:
            min_rank = 1000001
            if len(basisb_prefixes[domain]) == 0:
                continue
            for prefix in basisb_prefixes[domain]:
                if popularity_per_prefix[prefix] < min_rank and popularity_per_prefix[prefix] > 0:
                    min_rank = popularity_per_prefix[prefix]
            if min_rank == 1000001:
                popularity_per_domain[domain] = -1
            else:
                popularity_per_domain[domain] = min_rank

        write_json(f'../output/characteristics/popularity/{country_name}_domain2popularity.json', popularity_per_domain)

        sorted_values_prefixes = sorted(popularity_per_prefix.values())
        plot_heatmap(
            sorted_values_prefixes,
            f' {country_name.capitalize()} Critical BGP Prefixes Popularity',
            f"../output/characteristics/popularity/{country_name}_prefix2popularity.png"
        )

        sorted_values_domains = sorted(popularity_per_domain.values())
        plot_heatmap(
            sorted_values_domains,
            f'{country_name.capitalize()} Critical Domain Popularity',
            f"../output/characteristics/popularity/{country_name}_domain2popularity.png"
        )
        
        # Convert the data into a DataFrame
        df = pd.DataFrame(list(popularity_per_prefix.items()), columns=['Prefix', 'Value'])

        # Define the range bins and labels
        bins = [0, 100, 1000, 10000, 100000, 1000000]
        labels = ['0-100', '100-1000', '1000-10000', '10000-100000', '100000-1000000']

        # Categorize data into the specified ranges
        df['Range'] = pd.cut(df['Value'], bins=bins, labels=labels)

        # Add a separate category for -1
        df['Range'] = df['Range'].cat.add_categories('No Popularity (-1)')
        df.loc[df['Value'] == -1, 'Range'] = 'No Popularity (-1)'

        # Count the number of values in each range
        range_counts = df['Range'].value_counts().sort_index()

        # Convert the counts to a DataFrame for better presentation
        range_counts_df = range_counts.reset_index()
        range_counts_df.columns = ['Range', 'Count']

        # Add a column for the ratio
        total_count = range_counts_df['Count'].sum()
        range_counts_df['Ratio'] = range_counts_df['Count'] / total_count

        # Save the range counts DataFrame for this country
        range_counts_df.to_csv(f'../output/characteristics/popularity/{country_name}_range_counts.csv', index=False)

        # Calculate domain statistics
        df_domain = pd.DataFrame(list(popularity_per_domain.items()), columns=['Domain', 'Value'])
        total_domains = len(df_domain)
        popular_domains = len(df_domain[df_domain['Value'] > 0])
        
        # Add summary data for this country
        popular_prefix_count = range_counts_df.loc[range_counts_df['Range'] != 'No Popularity (-1)', 'Count'].sum()
        total_prefix_count = total_count
        summary_data.append({
            'Country': country_name,
            'Popular Prefixes (%)': (popular_prefix_count / total_prefix_count) * 100,
            'Popular Domains (%)': (popular_domains / total_domains) * 100
        })

    # Create a summary table for all countries
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv('../output/characteristics/popularity/summary_popular_prefixes_domains.csv', index=False)

    # Display the summary table
    print(summary_df)
