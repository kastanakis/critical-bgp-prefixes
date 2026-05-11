import json
import itertools

# Writes content to a JSON file
def write_json(jsonfilename, content):
    with open(jsonfilename, 'w') as fp:
        json.dump(content, fp, indent=4)

# Reads content of JSON file and returns it
def read_json(jsonfilename):
    with open(jsonfilename, 'r') as jsonfile:
        return json.load(jsonfile)

# Returns a flat list from a list of lists
def flatten_list(lista):
    return list(itertools.chain.from_iterable(lista))

# Function to count empty prefixes in a dictionary
def count_empty_prefixes(data_dict):
    return sum(1 for key, value in data_dict.items() if not value)  # Counts domains with no prefixes

if __name__ == '__main__':
    # Netherlands
    asn_per_domain_nl = read_json("../output/basisbeveiliging_parsed/domain2asn.json")
    ip_per_domain_nl = read_json("../output/basisbeveiliging_parsed/domain2ip.json")
    prefixes_per_domain_nl = read_json("../output/basisbeveiliging_parsed/domain2pfx_merged.json")

    # Bahamas
    asn_per_domain_bahamas = read_json("../output/hardenize_parsed/asns_per_country/bahamas-web-hygiene-dashboard_domain2asn.json")
    ip_per_domain_bahamas = read_json("../output/hardenize_parsed/ips_per_country/bahamas-web-hygiene-dashboard_domain2ip.json")
    prefixes_per_domain_bahamas = read_json("../output/hardenize_parsed/prefixes_per_country/bahamas-web-hygiene-dashboard_domain2pfx_routeviews.json")

    # Switzerland
    asn_per_domain_ch = read_json("../output/hardenize_parsed/asns_per_country/ch-resilience_domain2asn.json")
    ip_per_domain_ch = read_json("../output/hardenize_parsed/ips_per_country/ch-resilience_domain2ip.json")
    prefixes_per_domain_ch = read_json("../output/hardenize_parsed/prefixes_per_country/ch-resilience_domain2pfx_routeviews.json")

    # Estonia
    asn_per_domain_ee = read_json("../output/hardenize_parsed/asns_per_country/ee-tld_domain2asn.json")
    ip_per_domain_ee = read_json("../output/hardenize_parsed/ips_per_country/ee-tld_domain2ip.json")
    prefixes_per_domain_ee = read_json("../output/hardenize_parsed/prefixes_per_country/ee-tld_domain2pfx_routeviews.json")

    # Lithuania
    asn_per_domain_lithuania = read_json("../output/hardenize_parsed/asns_per_country/lithuania-dashboard_domain2asn.json")
    ip_per_domain_lithuania = read_json("../output/hardenize_parsed/ips_per_country/lithuania-dashboard_domain2ip.json")
    prefixes_per_domain_lithuania = read_json("../output/hardenize_parsed/prefixes_per_country/lithuania-dashboard_domain2pfx_routeviews.json")

    # Sweden
    asn_per_domain_sweden = read_json("../output/hardenize_parsed/asns_per_country/sweden-health-status_domain2asn.json")
    ip_per_domain_sweden = read_json("../output/hardenize_parsed/ips_per_country/sweden-health-status_domain2ip.json")
    prefixes_per_domain_sweden = read_json("../output/hardenize_parsed/prefixes_per_country/sweden-health-status_domain2pfx_routeviews.json")

    # Display stats for each country
    for country, asn_per_domain, ip_per_domain, prefixes_per_domain in [
        ('Netherlands', asn_per_domain_nl, ip_per_domain_nl, prefixes_per_domain_nl),
        ('Bahamas', asn_per_domain_bahamas, ip_per_domain_bahamas, prefixes_per_domain_bahamas),
        ('Switzerland', asn_per_domain_ch, ip_per_domain_ch, prefixes_per_domain_ch),
        ('Estonia', asn_per_domain_ee, ip_per_domain_ee, prefixes_per_domain_ee),
        ('Lithuania', asn_per_domain_lithuania, ip_per_domain_lithuania, prefixes_per_domain_lithuania),
        ('Sweden', asn_per_domain_sweden, ip_per_domain_sweden, prefixes_per_domain_sweden)
    ]:
        print(f"\n{country}")
        print(f"Unique Domains: {len(set(asn_per_domain.keys()))}")
        print(f"Unique IPs: {len(set(flatten_list(ip_per_domain.values())))}")
        print(f"Unique Prefixes: {len(set(flatten_list(prefixes_per_domain.values())))}")
        print(f"Unique ASNs: {len(set(flatten_list(asn_per_domain.values())))}")
        print(f"Non-routable Domain Ratio: {count_empty_prefixes(prefixes_per_domain)}")  # ✅ New Line for Empty Prefixes!
