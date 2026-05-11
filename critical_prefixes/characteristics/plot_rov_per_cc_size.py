import json
import ijson
import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint as pprint

FONT_SIZE = 15
plt.rcParams.update({'font.size': FONT_SIZE})

# Function to read JSON incrementally using ijson
def read_json_stream(jsonfilename, key=None):
    def generator(f):
        if key:
            yield from ijson.items(f, f'{key}.item')
        else:
            yield from ijson.kvitems(f, '')
    
    with open(jsonfilename, 'r') as f:
        yield from generator(f)

def read_json(jsonfilename):
    with open(jsonfilename, 'r') as jsonfile:
        return json.load(jsonfile)

def write_json(jsonfilename, content):
    with open(jsonfilename, 'w') as fp:
        json.dump(content, fp, indent=4)

def get_dutch_origins(prefixes_per_origin, prefixes):
    dutch_origin_to_business = set()
    for prefix in prefixes:
        origins = prefixes_per_origin[prefix]["origin"]
        for origin in origins:
            origin_asn = str(origin["asn"])
            dutch_origin_to_business.add(origin_asn)
    return list(dutch_origin_to_business)

if __name__ == '__main__':
    target_year_month = "2024-12"
    rov_per_as_dict = dict()
    prefixes_per_origin = {}
    
    # List of input files
    prefix_files = [
        "../output/characteristics/rpki/prefix2origin_bahamas.json",
        "../output/characteristics/rpki/prefix2origin_estonia.json",
        "../output/characteristics/rpki/prefix2origin_lithuania.json",
        "../output/characteristics/rpki/prefix2origin_netherlands.json",
        "../output/characteristics/rpki/prefix2origin_sweden.json",
        "../output/characteristics/rpki/prefix2origin_switzerland.json"
    ]
    
    # Merge all prefix2origin files
    for file in prefix_files:
        try:
            data = read_json(file)
            prefixes_per_origin.update(data)
        except Exception as e:
            print(f"Error reading {file}: {e}")
    
    cc_per_as = read_json("../../caida/20250101.customer-cones.json")
    prefixes = prefixes_per_origin.keys()
    dutch_origins = get_dutch_origins(prefixes_per_origin, prefixes)
    
    # Compile RoV per AS
    for asn, records in read_json_stream("../../rovista/rov_score_per_asn.json"):
        if records and "error" not in records:
            last_record = 0.0
            for record in records:
                if record["asnDateKey"]["recordDate"].startswith(target_year_month):
                    last_record = float(record['ratio'])  # Update to the latest as we iterate
            rov_per_as_dict[asn] = last_record
    
    # Collect CC per ROV
    cc_size_per_rov_score = dict()
    for asn in dutch_origins:
        if asn not in cc_per_as or asn not in rov_per_as_dict:
            continue
        customer_cone_size = len(cc_per_as[asn])
        rov_score = rov_per_as_dict[asn]
        if rov_score not in cc_size_per_rov_score:
            cc_size_per_rov_score[rov_score] = []
        cc_size_per_rov_score[rov_score].append(customer_cone_size)
    
    pprint(cc_size_per_rov_score)
    
    # Prepare data for the boxplot
    rov_scores = []
    boxplot_data = []
    
    for rov_score, cc_sizes in sorted(cc_size_per_rov_score.items()):
        cc_sizes = np.array(cc_sizes)
        cc_sizes = cc_sizes[cc_sizes > 0]  # Remove zeros
        if len(cc_sizes) > 0:
            rov_scores.append(rov_score)
            boxplot_data.append(cc_sizes)
    
    # Create the boxplot
    plt.figure(figsize=(12, 8))
    boxprops = dict(facecolor='grey', color='black')  # Set grey fill and black border
    plt.boxplot(boxplot_data, labels=rov_scores, patch_artist=True, boxprops=boxprops, showfliers=True)
    
    # Customize the plot
    plt.title('Boxplot of Customer Cone Sizes per ROV Score')
    plt.xlabel('ROV Score')
    plt.ylabel('Customer Cone Size')
    plt.yscale('log')  # Use log scale for better visualization of the size range
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig("../output/characteristics/rov/rov_per_cc_boxplot.png")
