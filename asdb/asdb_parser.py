import csv
import json

# Create a dictionary to store ASN and corresponding labels
asn_labels = {}

# Writes content to a JSON file
def write_json(jsonfilename, content):
    with open(jsonfilename, 'w+') as fp:
        json.dump(content, fp, indent=4)

# Use csv.DictReader to read the CSV file
unique_labels = set()
with open("2024-01_categorized_ases.csv", 'r') as csvfile:
    csvreader = csv.DictReader(csvfile)  # Automatically uses the first row as header
    for row in csvreader:
        # Get ASN and the labels (filter out empty strings)
        asn = row['ASN']
        # labels = list(set([label for label in row.values() if label][1:]))  # Collect non-empty labels
        labels = [label for label in list(row.values())[1:] if label]
        asn_labels[int(asn.strip("AS"))] = [labels[0]]  # Store in dictionary
        for labb in labels:
            unique_labels.add(labb)

# Output the resulting dictionary
write_json("2024-01_categorized_ases.json", asn_labels)
write_json("2024-01_labels_only.json", list(unique_labels))