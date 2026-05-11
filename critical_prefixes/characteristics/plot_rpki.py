import json
import matplotlib.pyplot as plt
import matplotlib
import os
import pandas as pd

# Set the global font size
matplotlib.rc('font', size=15)

# Reads content of JSON file and returns it
def read_json(jsonfilename):
    with open(jsonfilename, 'r') as jsonfile:
        return json.load(jsonfile)

# Define country-specific RPKI validation input files
rpki_inputs = [
    ("../output/characteristics/rpki/prefix2rpki_bahamas.json", "bahamas"),
    ("../output/characteristics/rpki/prefix2rpki_estonia.json", "estonia"),
    ("../output/characteristics/rpki/prefix2rpki_lithuania.json", "lithuania"),
    ("../output/characteristics/rpki/prefix2rpki_netherlands.json", "netherlands"),
    ("../output/characteristics/rpki/prefix2rpki_sweden.json", "sweden"),
    ("../output/characteristics/rpki/prefix2rpki_switzerland.json", "switzerland")
]

output_dir = "../output/characteristics/rpki/"
os.makedirs(output_dir, exist_ok=True)  # Ensure output directory exists

# Dictionary to store aggregated results
summary_table = {}

# Process each country separately
for filepath, country in rpki_inputs:
    print(f"\nProcessing RPKI validation for {country.upper()}...")

    # Load the RPKI validation data
    try:
        data = read_json(filepath)
    except FileNotFoundError:
        print(f"⚠ Skipping {country} - File not found: {filepath}")
        continue

    # Initialize counts for ROA status
    overall_counts = {"valid": 0, "invalid": 0, "unknown": 0}

    # Count RPKI statuses
    for prefix in data:
        if data[prefix] is None:
            status = "unknown"
        else:
            status = data[prefix].get('status', 'unknown').split('_')[0]

        if status in overall_counts:
            overall_counts[status] += 1
        else:
            overall_counts["unknown"] += 1  # Default to unknown for unexpected statuses

    # Compute total prefixes and percentages
    total_prefixes = sum(overall_counts.values())
    if total_prefixes > 0:
        valid_ratio = (overall_counts["valid"] / total_prefixes) * 100
        invalid_ratio = (overall_counts["invalid"] / total_prefixes) * 100
        unknown_ratio = (overall_counts["unknown"] / total_prefixes) * 100
    else:
        valid_ratio, invalid_ratio, unknown_ratio = 0, 0, 0  # Avoid division by zero

    # Store results in summary table
    summary_table[country] = {
        "Valid": overall_counts["valid"],
        "Valid (%)": round(valid_ratio, 2),
        "Invalid": overall_counts["invalid"],
        "Invalid (%)": round(invalid_ratio, 2),
        "Unknown": overall_counts["unknown"],
        "Unknown (%)": round(unknown_ratio, 2),
        "Total Prefixes": total_prefixes
    }

    # Prepare data for pie chart
    statuses = list(overall_counts.keys())
    counts = list(overall_counts.values())

    # Customize labels
    custom_labels = [f"{status.capitalize()} ({count})" for status, count in zip(statuses, counts)]

    # Define custom colors (Black = Valid, Gray = Invalid, White = Unknown)
    custom_colors = ["black", "gray", "white"]

    # Plotting the donut chart
    plt.figure(figsize=(8, 8))
    wedges, texts, autotexts = plt.pie(
        counts,
        labels=None,  # Remove labels from the pie itself
        autopct='%1.1f%%',
        startangle=140,
        colors=custom_colors,  # Apply custom colors
        wedgeprops={'edgecolor': 'black', 'linewidth': 1, 'width': 0.3},  # Add a hole
        textprops={'size': 15}  # Text size for percentages
    )

    # Add legend below the chart
    plt.legend(
        wedges,
        custom_labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.1),  # Center the legend horizontally, place it below the chart
        fontsize=15,
        ncol=len(custom_labels)  # Arrange all legend items in a single row
    )

    plt.title(f"RPKI Validation Status of {country.capitalize()} Prefixes")
    plt.tight_layout()
    
    # Save the figure
    save_path = os.path.join(output_dir, f"rpki_donut_chart_{country}.png")
    plt.savefig(save_path)
    plt.clf()  # Clear the current figure
    print(f"✅ Saved RPKI Donut Chart for {country}: {save_path}")

# Convert summary table to DataFrame
df_summary = pd.DataFrame.from_dict(summary_table, orient='index')
df_summary.index.name = "Country"

# Save summary table as CSV
csv_path = os.path.join(output_dir, "rpki_summary_table.csv")
df_summary.to_csv(csv_path)
print(f"✅ Saved RPKI Summary Table (CSV): {csv_path}")

# Save summary table as JSON
json_path = os.path.join(output_dir, "rpki_summary_table.json")
with open(json_path, 'w') as jsonfile:
    json.dump(summary_table, jsonfile, indent=4)
print(f"✅ Saved RPKI Summary Table (JSON): {json_path}")

print("\n✅ RPKI Processing Completed for All Countries!\n")
