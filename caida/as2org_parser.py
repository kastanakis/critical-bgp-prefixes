from pprint import pprint as pprint
import csv
import json

# Writes content to a json file
def write_json(jsonfilename, content):
    with open(jsonfilename, 'w+') as fp:
        json.dump(content, fp, indent=4)

# Maps ASes to Organizations
def as2org(as2rel_url, as2org_url):
    as2org_dict = dict()
    org_id2org_name = dict()
    public_asns = set()
    as2rel_dict = dict()

    # Unbox the as2rel dataset
    with open(as2rel_url, 'r') as csvfile:
        csvreader = csv.reader(csvfile, delimiter='|')
        for row in csvreader:
            if row[0][0] != '#':  # ignore lines starting with "#"
                as1 = int(row[0])
                as2 = int(row[1])
                rel = int(row[2])

                if as1 not in as2rel_dict:
                    as2rel_dict[as1] = list()
                as2rel_dict[as1].append([as2, rel])

                if as2 not in as2rel_dict:
                    as2rel_dict[as2] = list()
                as2rel_dict[as2].append([as1, -rel])

                # Add as1 and as2 in the public asns set
                public_asns.add(as1)
                public_asns.add(as2)
    public_asns_list = list(public_asns)

    # Unbox the as2org dataset
    with open(as2org_url, 'r') as csvfile:
        csvreader = csv.reader(csvfile, delimiter='|')
        rows = list(csvreader)
        for idx, row in enumerate(rows):
            print('Mapping ASes to Organizations {}\r'.format(idx/len(rows)), end='')
            if row[0][0] != '#':
                # For this format org_id|changed|name|country|source we will map the org_id with the respective org_name
                if(len(row) == 5):
                    org_id = str(row[0])
                    org_name = str(row[2])
                    org_id2org_name[org_id] = org_name
                # Consider only the entries in the following format: # format: aut|changed|aut_name|org_id|opaque_id|source 
                # but not this format: org_id|changed|name|country|source
                if(len(row) == 6):
                    asn = int(row[0])
                    as_name = str(row[2])
                    # If the ASn is not visible on the public internet discard the entry
                    if asn not in public_asns_list: 
                        continue
                    org_id = str(row[3])
                    org_name = org_id2org_name[org_id]
                    as2org_dict[str(asn) + "_" + as_name] = [org_id, org_name]
    return as2org_dict

if __name__ == '__main__':
    as2rel_url = "20241101.as-rel2.txt"
    as2org_url = "20241101.as-org2info.txt"
    as2org_dict = as2org(as2rel_url, as2org_url)
    write_json("20241101.as-org2info.json", as2org_dict)

    