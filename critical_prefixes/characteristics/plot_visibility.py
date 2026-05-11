import numpy as np
import matplotlib.pyplot as plt
import json
import pandas as pd

# Define global font size
FONT_SIZE = 15

# Reads content of JSON file and returns
def read_json(jsonfilename):
    with open(jsonfilename, 'r') as jsonfile:
        return json.load(jsonfile)

# List of countries
countries = ["estonia", "lithuania", "netherlands", "switzerland", "sweden"]

# Load random prefixes visibility data
random_prefixes_url = "../output/characteristics/visibility/random_1000_prefixes2visibility.json"
random_prefix_data = read_json(random_prefixes_url)

# Compute CDF for random prefixes
random_visibilities = np.sort(list(random_prefix_data.values()))
random_cdf = np.arange(1, len(random_visibilities) + 1) / len(random_visibilities)

# --------------------- Subplots: CDF for Each Country ---------------------
fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(15, 8))

# Aggregate all country visibilities for the unified CDF
all_country_visibilities = []

for i, country in enumerate(countries):
    url = f"../output/characteristics/visibility/{country}_domain2visibility.json"

    # Load visibility dataset
    data = read_json(url)

    # Step 1: Extract unique prefix visibilities
    unique_prefix_visibilities = {}
    for domain_data in data.values():
        for prefix, visibility in domain_data.items():
            if prefix not in unique_prefix_visibilities:
                unique_prefix_visibilities[prefix] = visibility

    # Collect all country-specific visibilities for the unified CDF
    all_country_visibilities.extend(unique_prefix_visibilities.values())

    # Step 2: Compute CDF for country-specific prefixes
    country_visibilities = np.sort(list(unique_prefix_visibilities.values()))
    country_cdf = np.arange(1, len(country_visibilities) + 1) / len(country_visibilities)

    # Step 3: Get the current subplot
    ax = axes[i // 3, i % 3]  # Calculate row and column indices

    # Step 4: Plot CDFs
    ax.plot(country_visibilities, country_cdf, marker='.', linestyle='-', label=f"{country.capitalize()} Prefixes", color="blue")
    ax.plot(random_visibilities, random_cdf, marker='.', linestyle='--', label="Random Prefixes", color="red")

    ax.set_xlabel("Visibility (%)", fontsize=FONT_SIZE)
    ax.set_ylabel("Cumulative Probability", fontsize=FONT_SIZE)
    ax.set_title(f"CDF for {country.capitalize()}", fontsize=FONT_SIZE)
    ax.grid(True)
    ax.legend()  # Add legend for distinction

# Adjust spacing between subplots
plt.tight_layout()
plt.savefig('../output/characteristics/visibility/all_countries_visibility_cdf_subplots.png', dpi=300)
print("✅ CDF subplots saved successfully!")

# --------------------- Unified CDF for All Countries vs Random Prefixes ---------------------
# Compute CDF for all country-specific prefixes combined
all_country_visibilities = np.sort(all_country_visibilities)
all_country_cdf = np.arange(1, len(all_country_visibilities) + 1) / len(all_country_visibilities)

# Create a new figure for the unified CDF
plt.figure(figsize=(8, 6))

# Plot unified CDFs
plt.plot(all_country_visibilities, all_country_cdf, marker='.', linestyle='-', label="Critical Prefixes", color="blue")
plt.plot(random_visibilities, random_cdf, marker='.', linestyle='--', label="Random Sample", color="red")

# Labels and formatting
plt.xlabel("Visibility (%)", fontsize=FONT_SIZE)
plt.ylabel("CDF", fontsize=FONT_SIZE)
plt.title("Critical BGP Prefixes vs Random Prefixes", fontsize=FONT_SIZE)
plt.grid(True)
plt.legend()

# Save the figure
plt.savefig('../output/characteristics/visibility/unified_visibility_cdf.png', dpi=300)
print("✅ Unified CDF saved successfully!")
