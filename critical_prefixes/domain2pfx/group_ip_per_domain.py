import csv
import json
import sys

# Writes content to a JSON file
def write_json(jsonfilename, content):
    with open(jsonfilename, 'w+') as fp:
        json.dump(content, fp, indent=4)

# Processes IPv4 and IPv6 files to populate a dictionary with names as keys and IPs as values
def process_files(ipv4_filepath, ipv6_filepath, output_filepath):
    mapper = dict()
    
    # Read the IPv4 and IPv6 files
    with open(ipv4_filepath, 'r') as ipv4_file, open(ipv6_filepath, 'r') as ipv6_file:
        ipv4 = csv.reader(ipv4_file, delimiter=" ")
        ipv6 = csv.reader(ipv6_file, delimiter=" ")

        # Populate the dictionary with IPv4 data
        for row in ipv4:
            name = row[0].rstrip('.')
            type = row[1]
            if type != "A": continue  # Discard non-IPv4 entries
            ip = row[2]
            if name not in mapper:
                mapper[name] = []
            if ip not in mapper[name]:  # Add unique IPs only
                mapper[name].append(ip)
        
        # Populate the dictionary with IPv6 data
        for row in ipv6:
            name = row[0].rstrip('.')
            type = row[1]
            if type != "AAAA": continue  # Discard non-IPv6 entries
            ip = row[2]
            if name not in mapper:
                mapper[name] = []
            if ip not in mapper[name]:  # Add unique IPs only
                mapper[name].append(ip)

    print(f"Total unique domains processed: {len(mapper.keys())}")
    write_json(output_filepath, mapper)

# Processes IPv4 and IPv6 files to populate a dictionary with names as keys and IPs as values
def process_hardenize_files(ipv4_filepaths, ipv6_filepaths, output_dir):
    for idx, ipv4_filepath in enumerate(ipv4_filepaths):
        mapper = dict()
        output_filename = ipv4_filepath.split("domains_per_country/")[1].split("_ipv4.txt")[0]
        # Read the IPv4 and IPv6 files
        with open(ipv4_filepath, 'r') as ipv4_file, open(ipv6_filepaths[idx], 'r') as ipv6_file:
            ipv4 = csv.reader(ipv4_file, delimiter=" ")
            ipv6 = csv.reader(ipv6_file, delimiter=" ")

            # Populate the dictionary with IPv4 data
            for row in ipv4:
                name = row[0].rstrip('.')
                type = row[1]
                if type != "A": continue  # Discard non-IPv4 entries
                ip = row[2]
                if name not in mapper:
                    mapper[name] = []
                if ip not in mapper[name]:  # Add unique IPs only
                    mapper[name].append(ip)
            
            # Populate the dictionary with IPv6 data
            for row in ipv6:
                name = row[0].rstrip('.')
                type = row[1]
                if type != "AAAA": continue  # Discard non-IPv6 entries
                ip = row[2]
                if name not in mapper:
                    mapper[name] = []
                if ip not in mapper[name]:  # Add unique IPs only
                    mapper[name].append(ip)

        print(f"Total unique domains processed: {len(mapper.keys())}")
        write_json(output_dir + output_filename + "_domain2ip.json", mapper)    

if __name__ == "__main__":
    # Check if the user has provided the dataset argument
    if len(sys.argv) != 2:
        print("Usage: python script.py <dataset>")
        print("Available datasets: basisbeveiliging, tranco, hardenize")
        sys.exit(1)

    # Get the dataset choice from command-line arguments
    dataset_choice = sys.argv[1].lower()

    # Define file paths for each dataset
    datasets = {
        "basisbeveiliging": {
            "ipv4_filepath": "../output/basisbeveiliging_parsed/all_basisbeveiliging_ipv4.txt",
            "ipv6_filepath": "../output/basisbeveiliging_parsed/all_basisbeveiliging_ipv6.txt",
            "output_filepath": "../output/basisbeveiliging_parsed/domain2ip.json"
        },
        "tranco": {
            "ipv4_filepath": "../output/tranco_parsed/all_tranco_ipv4.txt",
            "ipv6_filepath": "../output/tranco_parsed/all_tranco_ipv6.txt",
            "output_filepath": "../output/tranco_parsed/domain2ip.json"
        },
        "hardenize": {
            "ipv4_filepaths": ["../output/hardenize_parsed/domains_per_country/bahamas-web-hygiene-dashboard_ipv4.txt", \
                               "../output/hardenize_parsed/domains_per_country/ch-resilience_ipv4.txt", \
                               "../output/hardenize_parsed/domains_per_country/ee-tld_ipv4.txt", \
                               "../output/hardenize_parsed/domains_per_country/global-top-sites_ipv4.txt", \
                               "../output/hardenize_parsed/domains_per_country/lithuania-dashboard_ipv4.txt", \
                               "../output/hardenize_parsed/domains_per_country/sweden-health-status_ipv4.txt"],
            "ipv6_filepaths": ["../output/hardenize_parsed/domains_per_country/bahamas-web-hygiene-dashboard_ipv6.txt", \
                               "../output/hardenize_parsed/domains_per_country/ch-resilience_ipv6.txt", \
                               "../output/hardenize_parsed/domains_per_country/ee-tld_ipv6.txt", \
                               "../output/hardenize_parsed/domains_per_country/global-top-sites_ipv6.txt", \
                               "../output/hardenize_parsed/domains_per_country/lithuania-dashboard_ipv6.txt", \
                               "../output/hardenize_parsed/domains_per_country/sweden-health-status_ipv6.txt"],
            "output_dir": "../output/hardenize_parsed/ips_per_country/"
        }
    }

    # Check if the dataset choice is valid
    if dataset_choice not in datasets:
        print("Invalid dataset choice. Available options are: basisbeveiliging, tranco, hardenize")
        sys.exit(1)

    # Process the selected dataset
    selected_dataset = datasets[dataset_choice]
    # Process the selected dataset
    if dataset_choice == "tranco" or dataset_choice == "basisbeveiliging":
        process_files(
            selected_dataset["ipv4_filepath"],
            selected_dataset["ipv6_filepath"],
            selected_dataset["output_filepath"]
        )
    elif dataset_choice == "hardenize":
        process_hardenize_files(
            selected_dataset["ipv4_filepaths"],
            selected_dataset["ipv6_filepaths"],
            selected_dataset["output_dir"]
        )
