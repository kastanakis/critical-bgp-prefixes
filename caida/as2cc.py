import csv
import json
from pprint import pprint as pprint
from collections import defaultdict

# Writes content to a JSON file
def write_json(jsonfilename, content):
    with open(jsonfilename, 'w') as fp:
        json.dump(content, fp, indent=4)

def extract_customer_cones(as2rel_url):
    customers = defaultdict(list)

    # Unbox the as2rel dataset
    with open(as2rel_url, 'r') as csvfile:
        csvreader = csv.reader(csvfile, delimiter='|')
        for row in csvreader:
            if row[0][0] != '#':  # Ignore lines starting with "#"
                as1 = str(row[0])
                as2 = str(row[1])
                rel = int(row[2])

                # If rel == -1 this means that as1 is the provider of as2
                if rel == -1:
                    customers[as1].append(as2)  # Reverse the relationship to track customers of as1

    # Compute customer cones
    customer_cones = {as_id: set() for as_id in customers}

    def compute_cone(as_id):
        if as_id in customer_cones and customer_cones[as_id]:  # Already computed
            return customer_cones[as_id]
        cone = set(customers.get(as_id, []))  # Direct customers
        for customer in customers.get(as_id, []):
            cone.update(compute_cone(customer))  # Recursive customers
        customer_cones[as_id] = cone
        return cone

    for as_id in customers:
        compute_cone(as_id)

    # Convert sets to sorted lists for JSON compatibility
    customer_cones = {k: sorted(v) for k, v in customer_cones.items()}
    
    return customer_cones

customer_cones = extract_customer_cones("20250101.as-rel2.txt")
write_json("20250101.customer-cones.json", customer_cones)
