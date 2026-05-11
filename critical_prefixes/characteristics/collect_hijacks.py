import json
import requests
from datetime import datetime

# List of country-specific ASN JSON files
domain2asn_inputs = [
    ("../output/basisbeveiliging_parsed/domain2asn.json", "netherlands"),
    ("../output/hardenize_parsed/asns_per_country/bahamas-web-hygiene-dashboard_domain2asn.json", "bahamas"),
    ("../output/hardenize_parsed/asns_per_country/ch-resilience_domain2asn.json", "switzerland"),
    ("../output/hardenize_parsed/asns_per_country/ee-tld_domain2asn.json", "estonia"),
    ("../output/hardenize_parsed/asns_per_country/lithuania-dashboard_domain2asn.json", "lithuania"),
    ("../output/hardenize_parsed/asns_per_country/sweden-health-status_domain2asn.json", "sweden"),
]

# Full year 2024
start_time = "2024-01-01T00:00"
end_time = "2024-12-31T23:59"

# API template
API_URL_TEMPLATE = (
    "https://api.grip.inetintel.cc.gatech.edu/json/events?length=100&start=0"
    "&ts_start={start_time}&ts_end={end_time}&min_susp=80&max_susp=100"
    "&event_type=moas&asns={asn_str}"
)

def get_unique_asns(file_path):
    """Load unique ASNs from a JSON file."""
    with open(file_path, "r") as file:
        data = json.load(file)
    return list(set(asn for asn_list in data.values() for asn in asn_list))

def fetch_hijacks(asn_list):
    """Fetch hijack data for a batch of ASNs."""
    # If the API doesn't accept multiple ASNs, iterate over each ASN
    hijack_data = {}
    
    for asn in asn_list:
        asn_str = str(asn)
        api_url = API_URL_TEMPLATE.format(start_time=start_time, end_time=end_time, asn_str=asn_str)
        
        print(f"Calling API with URL: {api_url}")  # Debugging: Print the URL being called
        
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json().get("data", {})
                
                hijack_data[asn] = data  # Save the hijack data for this ASN
            else:
                print(f"⚠️ API failed for ASN {asn_str} (Status {response.status_code})")
        except requests.RequestException as e:
            print(f"⚠️ API request error: {e}")
    
    return hijack_data

def process_country(file_path, country_label):
    """Process ASN hijacks per country."""
    print(f"\n=== Processing {country_label} ===")
    
    unique_asns = get_unique_asns(file_path)
    if not unique_asns:
        print(f"⚠️ No ASNs found for {country_label}")
        return

    batch_size = 10  # Adjust the batch size if needed
    suspicious_time_asn = {}

    for i in range(0, len(unique_asns), batch_size):
        batch_asns = unique_asns[i:i + batch_size]
        hijack_data = fetch_hijacks(batch_asns)

        if not hijack_data:
            continue  # Skip if no hijack events found

        for asn, events in hijack_data.items():
            suspicious_time_asn[asn] = {
                "total_number_of_events": len(events),
                "event_details": [
                    {
                        "start": datetime.fromtimestamp(event["view_ts"]).strftime("%Y-%m-%d %H:%M:%S"),
                        "end": (
                            datetime.fromtimestamp(event["finished_ts"]).strftime("%Y-%m-%d %H:%M:%S")
                            if event["finished_ts"] else "Ongoing"
                        ),
                        "prefixes": event.get("summary", {}).get("prefixes", [])
                    }
                    for event in events
                ],
            }

    # Save results
    output_path = f"../output/characteristics/hijacks/{country_label}_asn_grip_moas_2024.json"
    with open(output_path, "w") as outfile:
        json.dump(suspicious_time_asn, outfile, indent=2)

    print(f"✅ Completed {country_label}, saved to {output_path}")

# Run for all countries
for file_path, country_label in domain2asn_inputs:
    process_country(file_path, country_label)

