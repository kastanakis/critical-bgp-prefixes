import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import plotly.express as px
from PIL import Image, ImageDraw
import os
import pycountry

COLOR_SCALE = "Reds"

# Reads content of JSON file and returns
def read_json(jsonfilename):
    with open(jsonfilename, 'r') as jsonfile:
        return json.load(jsonfile)

# Converts ISO2 to ISO3
def iso2_to_iso3(iso2):
    try:
        return pycountry.countries.get(alpha_2=iso2).alpha_3
    except AttributeError:
        return None

# Datasets
countries = ["estonia", "lithuania", "netherlands", "switzerland", "sweden"]
output_dir = "../output/characteristics/geolocation/"

for country in countries:
    url = output_dir + country + "_prefix2location.json"

    # Load geolocation dataset
    data = read_json(url)

    # Step 1: Flatten and count occurrences
    all_isocodes = [iso for prefixes in data.values() for iso in prefixes]
    frequency = pd.Series(all_isocodes).value_counts().reset_index()
    frequency.columns = ['isocode', 'count']

    # Step 2: Convert ISO-2 to ISO-3 codes
    frequency['iso3'] = frequency['isocode'].apply(iso2_to_iso3)
    frequency = frequency.dropna()

    # Step 3: Plot Europe Map
    fig_europe = px.choropleth(
        frequency,
        locations="iso3",
        color="count",
        labels={"count": "Prefix Count"},
        locationmode="ISO-3",
        scope="europe",
        color_continuous_scale=COLOR_SCALE
    )
    fig_europe.write_image(output_dir + country + "_prefix2location_europe_map.png")

    # Step 4: Plot US Map
    fig_us = px.choropleth(
        frequency,
        locations="iso3",
        color="count",
        labels={"count": "Prefix Count"},
        locationmode="ISO-3",
        scope="north america",
        color_continuous_scale=COLOR_SCALE
    )
    fig_us.write_image(output_dir + country + "_prefix2location_us_map.png")

# --- Top Half ---
top_countries = countries[:3]
fig_top, axes_top = plt.subplots(2, 3, figsize=(18, 12))
for idx, country in enumerate(top_countries):
    emap = Image.open(output_dir + f"{country}_prefix2location_europe_map.png")
    umap = Image.open(output_dir + f"{country}_prefix2location_us_map.png")
    axes_top[0, idx].imshow(emap)
    axes_top[0, idx].axis('off')
    axes_top[0, idx].set_title(f"(a{idx+1}) {country.capitalize()} - Europe Map", fontsize=14)
    axes_top[1, idx].imshow(umap)
    axes_top[1, idx].axis('off')
    axes_top[1, idx].set_title(f"(b{idx+1}) {country.capitalize()} - US Map", fontsize=14)
fig_top.tight_layout()
fig_top_path = output_dir + "_top_half.png"
fig_top.savefig(fig_top_path, dpi=300)
plt.close(fig_top)

# --- Bottom Half ---
bottom_countries = countries[3:]
fig_bottom, axes_bottom = plt.subplots(2, 2, figsize=(12, 8))
for idx, country in enumerate(bottom_countries):
    emap = Image.open(output_dir + f"{country}_prefix2location_europe_map.png")
    umap = Image.open(output_dir + f"{country}_prefix2location_us_map.png")
    axes_bottom[0, idx].imshow(emap)
    axes_bottom[0, idx].axis('off')
    axes_bottom[0, idx].set_title(f"(c{idx+1}) {country.capitalize()} - Critical Prefixes in Europe", fontsize=14)
    axes_bottom[1, idx].imshow(umap)
    axes_bottom[1, idx].axis('off')
    axes_bottom[1, idx].set_title(f"(d{idx+1}) {country.capitalize()} - Critical Prefixes in US", fontsize=14)
fig_bottom.tight_layout()
fig_bottom_path = output_dir + "_bottom_half.png"
fig_bottom.savefig(fig_bottom_path, dpi=300)
plt.close(fig_bottom)

# --- Merge Final Canvas ---
top_img = Image.open(fig_top_path)
bottom_img = Image.open(fig_bottom_path)

# Determine canvas width and height
canvas_width = max(top_img.width, bottom_img.width + int(0.5 * bottom_img.width))
canvas_height = top_img.height + bottom_img.height
canvas = Image.new("RGB", (canvas_width, canvas_height), (255, 255, 255))

# Paste top at the top, bottom centered
canvas.paste(top_img, (0, 0))
bottom_x = (canvas_width - bottom_img.width) // 2
canvas.paste(bottom_img, (bottom_x, top_img.height))

canvas.save(output_dir + "split_combined_maps.png")