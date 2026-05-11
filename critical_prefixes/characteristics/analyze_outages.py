import json
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator

# Load the JSON file
with open("../output/characteristics/outages/down_time_per_asn_unified.json", "r") as f:
    data = json.load(f)

asn_outage_counts = {}
asn_outage_durations = {}

# Loop through all countries and ASNs
for country, asns in data.items():
    if country == 'bahamas': 
        print("Bahamas out")
        continue
    for asn, outage_data in asns.items():
        count = outage_data[0]["total_down_times"]
        durations = [entry["duration"] for entry in outage_data[1]]
        total_duration = sum(durations)

        asn = str(asn)
        asn_outage_counts[asn] = count
        asn_outage_durations[asn] = total_duration

# Get top N ASNs by either count or duration
# N = 200
top_outage_counts = sorted(asn_outage_counts.items(), key=lambda x: x[1], reverse=True)
top_outage_durations = sorted(asn_outage_durations.items(), key=lambda x: x[1], reverse=True)

# Union of top ASNs
top_asns = set([asn for asn, _ in top_outage_counts] + [asn for asn, _ in top_outage_durations])

# Prepare data for plotting
x = []  # outage counts
y = []  # total durations in hours
labels = []

for asn in top_asns:
    count = asn_outage_counts.get(asn, 0)
    duration_hours = asn_outage_durations.get(asn, 0) / 3600
    x.append(count)
    y.append(duration_hours)
    labels.append(asn)

plt.figure(figsize=(10, 8))

# Log scales to handle wide spread
plt.xscale("log")
# plt.yscale("log")

# Normalize size & color by duration
sizes = [max(val, 1) * 0.7 for val in y]
colors = y  # color map by duration

# Scatter plot
scatter = plt.scatter(x, y, s=sizes, c=colors, cmap="plasma", alpha=0.85,
                      edgecolors="black", vmax=1000, linewidth=0.4)

# Label a few impactful ASNs (not all)
impact_scores = [(i, x[i] * y[i]) for i in range(len(x))]
impact_scores.sort(key=lambda item: item[1], reverse=True)
top_indices = [i for i, _ in impact_scores[:12]]

for i in top_indices:
    plt.annotate(labels[i], (x[i], y[i]),
                 textcoords="offset points", xytext=(6, 5),
                 ha='left', fontsize=14, weight='bold',
                 bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="gray", lw=0.5, alpha=0.8))

# Axes & title
plt.xlabel("Number of Outages (log scale)", fontsize=16)
plt.ylabel("Total Duration (Hours)", fontsize=16)
plt.ylim(top=1000)
# plt.title("Critical AS Outages – Frequency vs. Duration (Nov 2024)", fontsize=16)

# Grid + Colorbar
# plt.grid(True, which="both", linestyle="--", linewidth=0.4, alpha=0.7)
# Add more grid lines (major + minor)
plt.minorticks_on()
plt.grid(True, which="major", linestyle="--", linewidth=0.5, alpha=0.8)
plt.grid(True, which="minor", linestyle=":", linewidth=0.4, alpha=0.5)

# Customize minor tick locations for log x-axis
plt.gca().xaxis.set_minor_locator(LogLocator(base=10.0, subs='auto', numticks=100))

cbar = plt.colorbar(scatter, orientation='horizontal', pad=0.15)
cbar.set_label("Total Duration (hrs)")

plt.tight_layout()
plt.savefig("../output/characteristics/outages/count_vs_duration.png")
