import csv
import json
import glob
import os
import sys

# Finds all JSON files in a directory
def read_all_json_files_in_a_dir(directory_path):
    return glob.glob(os.path.join(directory_path, '*.json'))

# Reads and returns the content of a JSON file
def read_json(jsonfilename):
    with open(jsonfilename, 'r') as jsonfile:
        return json.load(jsonfile)

# Writes content to a JSON file
def write_json(jsonfilename, content):
    with open(jsonfilename, 'w+') as fp:
        json.dump(content, fp, indent=4)

# Reads a CSV file and returns a list of second column entries (domains)
def read_csv(filename):
    with open(filename, 'r') as csvfile_in:
        tranco_in = csv.reader(csvfile_in, delimiter=',')
        return [line[1] for line in tranco_in]

# Writes a list of content to a CSV file
def write_csv(filename, content):
    with open(filename, 'w+') as csvfile_out:
        tranco_out = csv.writer(csvfile_out, delimiter='\n')
        tranco_out.writerows([[line] for line in content])

# Processes Tranco dataset CSV
def process_tranco_dataset(input_csv_path, output_csv_path):
    all_tranco_domains = [item for item in read_csv(input_csv_path)]
    write_csv(output_csv_path, all_tranco_domains)
    print(f"Processed Tranco dataset with {len(all_tranco_domains)} domains.")

# Processes Basisbeveiliging dataset JSON
def process_basisbeveiliging_dataset(input_json_dir, output_csv_path):
    all_dutch_candidate_critical_domains = []
    bas_domain_types = read_all_json_files_in_a_dir(input_json_dir)
    for domain_type in bas_domain_types:
        content = read_json(domain_type)
        for idx, item in enumerate(content['data']):
            if idx == 0: continue  # Skip headers if present
            url = item[1]
            all_dutch_candidate_critical_domains.append(url)
    write_csv(output_csv_path, all_dutch_candidate_critical_domains)
    print(f"Processed Basisbeveiliging dataset with {len(all_dutch_candidate_critical_domains)} domains.")

# Processes Hardenize dataset JSON
def process_hardenize_dataset(input_json_dir, output_csv_path):
    hardenize_domains_per_country = read_all_json_files_in_a_dir(input_json_dir)
    for domain_type in hardenize_domains_per_country:
        all_hardenize_critical_domains = []
        country = domain_type.split("critical_domains_")[1].split(".json")[0]
        content = read_json(domain_type)
        for item in content:
            all_hardenize_critical_domains.append(item)
        write_csv(output_csv_path + country + "_domains.csv", all_hardenize_critical_domains)
    print(f"Processed Hardenize dataset for {len(hardenize_domains_per_country)} countries.")


if __name__ == "__main__":
    # Check for command-line arguments
    if len(sys.argv) != 2:
        print("Usage: python script.py <dataset>")
        print("Available datasets: basisbeveiliging, tranco, hardenize")
        sys.exit(1)

    # Dataset choice
    dataset_choice = sys.argv[1].lower()

    # File paths for each dataset
    datasets = {
        "tranco": {
            "input_csv_path": "../../tranco/top-1m_november_2024.csv",
            "output_csv_path": "../output/tranco_parsed/all_tranco_domains.csv"
        },
        "basisbeveiliging": {
            "input_json_dir": "../../basisbeveiliging/domains/",
            "output_csv_path": "../output/basisbeveiliging_parsed/all_basibeveiliging_domains.csv"
        },
        "hardenize": {
            "input_json_dir": "../../hardenize/",
            "output_csv_dir": "../output/hardenize_parsed/domains_per_country/"
        }
    }

    # Validate dataset choice
    if dataset_choice not in datasets:
        print("Invalid dataset choice. Available options are: basisbeveiliging, tranco, hardenize")
        sys.exit(1)

    # Process the selected dataset
    if dataset_choice == "tranco":
        process_tranco_dataset(datasets["tranco"]["input_csv_path"], datasets["tranco"]["output_csv_path"])
    elif dataset_choice == "basisbeveiliging":
        process_basisbeveiliging_dataset(datasets["basisbeveiliging"]["input_json_dir"], datasets["basisbeveiliging"]["output_csv_path"])
    elif dataset_choice == "hardenize":
        process_hardenize_dataset(datasets["hardenize"]["input_json_dir"], datasets["hardenize"]["output_csv_dir"])