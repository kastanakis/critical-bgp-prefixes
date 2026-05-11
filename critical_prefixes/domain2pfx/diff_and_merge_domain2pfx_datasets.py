import json
from pprint import pprint as pprint
from collections import OrderedDict

def merge_datasets(dataset1, dataset2):
    merged_dataset = OrderedDict()

    # First, add keys from dataset1, preserving value order and removing duplicates
    for key in dataset1:
        merged_values = dataset1[key] + [v for v in dataset2.get(key, []) if v not in dataset1[key]]
        merged_dataset[key] = merged_values

    # Then, add keys from dataset2 that are not in dataset1, preserving order
    for key in dataset2:
        if key not in merged_dataset:
            merged_dataset[key] = dataset2[key]

    return merged_dataset

# Reads content of JSON file and returns
def read_json(jsonfilename):
    with open(jsonfilename, 'r') as jsonfile:
        return json.load(jsonfile)

# writes content to json file
def write_json(jsonfilename, content):
    with open(jsonfilename, 'w+') as fp:
        json.dump(content, fp, indent=4)

# Finds differences between the produced domain2pfx datasets
def find_differences(dataset1, dataset2):
    # Initialize dictionaries to store differences
    missing_in_dataset1 = {}
    missing_in_dataset2 = {}
    different_values = {}

    # Find keys that are only in one of the datasets
    keys_in_dataset1_not_in_dataset2 = set(dataset1.keys()) - set(dataset2.keys())
    keys_in_dataset2_not_in_dataset1 = set(dataset2.keys()) - set(dataset1.keys())

    # Add these to missing dictionaries
    for key in keys_in_dataset1_not_in_dataset2:
        missing_in_dataset2[key] = dataset1[key]
    for key in keys_in_dataset2_not_in_dataset1:
        missing_in_dataset1[key] = dataset2[key]

    # For keys that are present in both datasets, compare their values
    for key in dataset1.keys() & dataset2.keys():
        if set(dataset1[key]) != set(dataset2[key]):
            different_values[key] = {
                "dataset1": dataset1[key],
                "dataset2": dataset2[key]
            }

    return {
        "missing_in_dataset1": missing_in_dataset1,
        "missing_in_dataset2": missing_in_dataset2,
        "different_values": different_values
    }

if __name__ == '__main__':
    ds1 = read_json("../output/basisbeveiliging_parsed/domain2pfx_ripestat.json")
    ds2 = read_json("../output/basisbeveiliging_parsed/domain2pfx_routeviews.json")
    print('{} domains have resolved to different IP prefixes through RipeStat and RouteViews'.format(str(len(find_differences(ds1, ds2)['different_values'].keys()))))
    merged = merge_datasets(ds1, ds2)
    write_json("../output/basisbeveiliging_parsed/domain2pfx_merged.json", merged)

    ds1_unc = read_json("../output/basisbeveiliging_parsed/domain2pfx_ripestat_uncovered.json")
    ds2_unc = read_json("../output/basisbeveiliging_parsed/domain2pfx_routeviews_uncovered.json")
    merged_unc = merge_datasets(ds1_unc, ds2_unc)
    write_json("../output/basisbeveiliging_parsed/domain2pfx_uncovered_merged.json", merged_unc)



