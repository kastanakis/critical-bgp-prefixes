import os
import json
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator

# === CONFIG ===
HIJACK_DIR = "../output/characteristics/hijacks"
END_OF_YEAR = datetime.strptime("2024-12-31 23:59:00", "%Y-%m-%d %H:%M:%S")
SCENARIO = "ignore_ongoing"
LABEL = "Ignore Ongoing Events"
FILENAME = "count_vs_duration_ignore_ongoing"

# === FUNCTIONS ===
def load_all_hijack_data():
    combined = {}
    for fname in os.listdir(HIJACK_DIR):
        if fname.split("_")[0] == "bahamas": 
            continue
        if fname.endswith(".json"):
            with open(os.path.join(HIJACK_DIR, fname), "r") as f:
                country_data = json.load(f)
                for asn, details in country_data.items():
                    if asn not in combined:
                        combined[asn] = details["event_details"]
    return combined

def compute_metrics(hijack_data, scenario):
    count_per_asn = {}
    duration_per_asn = {}

    for asn, events in hijack_data.items():
        count = 0
        total_duration = 0
        for event in events:
            start = datetime.strptime(event["start"], "%Y-%m-%d %H:%M:%S")
            end_str = event["end"]

            if end_str == "Ongoing":
                if scenario == "ignore_ongoing":
                    continue
                elif scenario == "ongoing_as_zero":
                    duration = 0
                elif scenario == "ongoing_until_end":
                    if start > END_OF_YEAR:
                        continue  # Skip invalid future-starting events
                    duration = (END_OF_YEAR - start).total_seconds()
            else:
                end = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")
                duration = (end - start).total_seconds()

            count += 1
            total_duration += duration

        count_per_asn[asn] = count
        duration_per_asn[asn] = total_duration

    return count_per_asn, duration_per_asn

def plot_hijack_analysis(counts, durations, title, filename):
    x, y, labels = [], [], []

    for asn in set(counts) | set(durations):
        count = counts.get(asn, 0)
        duration_hours = durations.get(asn, 0) / 3600
        x.append(count)
        y.append(duration_hours)
        labels.append(asn)

    sizes = [max(val, 1) * 0.7 for val in y]
    colors = y

    plt.figure(figsize=(10, 8))
    plt.xscale("log")
    scatter = plt.scatter(x, y, s=sizes, c=colors, cmap="plasma", alpha=0.85,
                          edgecolors="black", vmax=1000, linewidth=0.4)

    impact_scores = [(i, x[i] * y[i]) for i in range(len(x))]
    impact_scores.sort(key=lambda item: item[1], reverse=True)
    top_indices = [i for i, _ in impact_scores[:12]]

    for i in top_indices:
        plt.annotate(labels[i], (x[i], y[i]), textcoords="offset points", xytext=(6, 5),
                     ha='left', fontsize=16, weight='bold',
                     bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="gray", lw=0.5, alpha=0.8))

    plt.xlabel("Number of Hijacks (log scale)", fontsize=16)
    plt.ylabel("Total Duration (Hours)", fontsize=16)
    plt.ylim(top=1000)
    plt.minorticks_on()
    plt.grid(True, which="major", linestyle="--", linewidth=0.5, alpha=0.8)
    plt.grid(True, which="minor", linestyle=":", linewidth=0.4, alpha=0.5)
    plt.gca().xaxis.set_minor_locator(LogLocator(base=10.0, subs='auto', numticks=100))

    cbar = plt.colorbar(scatter, orientation='horizontal', pad=0.15)
    cbar.set_label("Total Duration (hrs)")

    plt.title(title, fontsize=16)
    plt.tight_layout()
    plt.savefig(f"../output/characteristics/hijacks/{filename}.png")
    plt.close()

# === MAIN ===
hijack_data = load_all_hijack_data()
counts, durations = compute_metrics(hijack_data, SCENARIO)
plot_hijack_analysis(counts, durations, f"Hijack Events – {LABEL}", FILENAME)

print("Top 10 ASNs by number of hijacks:")
for asn, count in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"ASN {asn}: {count} hijacks")
