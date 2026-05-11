import json
import os
import asyncio
import aiohttp
from tqdm.asyncio import tqdm
from multiprocessing import Pool, cpu_count

# File locations
domain2ip_files = [
    "../output/basisbeveiliging_parsed/domain2ip.json",
    "../output/hardenize_parsed/ips_per_country/bahamas-web-hygiene-dashboard_domain2ip.json",
    "../output/hardenize_parsed/ips_per_country/ch-resilience_domain2ip.json",
    "../output/hardenize_parsed/ips_per_country/ee-tld_domain2ip.json",
    "../output/hardenize_parsed/ips_per_country/lithuania-dashboard_domain2ip.json",
    "../output/hardenize_parsed/ips_per_country/sweden-health-status_domain2ip.json",
]

# Load domain-to-IP mappings
def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    return {}

# Use multiprocessing to load JSON files faster
with Pool(cpu_count()) as pool:
    domain2ip_data = pool.map(load_json, domain2ip_files)

# Extract unique domains & normalize them (remove "www." safely)
unique_domains = set()
domain_ip_mapping = {}  # Store domain-to-IP mappings

for data in domain2ip_data:
    for domain, ip_list in data.items():
        clean_domain = domain[4:] if domain.startswith("www.") else domain
        unique_domains.add(clean_domain)
        domain_ip_mapping[clean_domain] = ip_list  # Save domain-IP mappings

print(f"Total unique domains found: {len(unique_domains)}")

# Convert to list for async processing
unique_domains = list(unique_domains)

# Define valid HTTP status codes that mean a site is "online"
VALID_HTTP_CODES = {200, 301, 302, 401, 403, 503}

# Async function to check website status
async def check_website(domain, semaphore):
    """Check if a website is online by testing both 'www.' and non-www versions."""
    async with semaphore:
        urls = [f"https://{domain}", f"https://www.{domain}"]
        for url in urls:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=10, allow_redirects=True) as response:
                        if response.status in VALID_HTTP_CODES:
                            return domain, True  # Online if status is valid
            except (aiohttp.ClientError, asyncio.TimeoutError):
                continue  # Try the next version if one fails
    return domain, False  # Mark as offline only if both fail

# Main async function with a real-time progress bar
async def check_all_websites():
    semaphore = asyncio.Semaphore(500)  # Create semaphore inside the function

    tasks = [asyncio.create_task(check_website(domain, semaphore)) for domain in unique_domains]

    results = []
    for future in tqdm(asyncio.as_completed(tasks), total=len(unique_domains), desc="Checking Websites", ncols=80):
        result = await future
        results.append(result)

    return results

# Run the async website checker
results = asyncio.run(check_all_websites())

# Classify results
online_sites = {domain for domain, is_online in results if is_online}
offline_sites = {domain for domain, is_online in results if not is_online}

# Save online & offline sites
def write_json(jsonfilename, content):
    with open(jsonfilename, 'w') as fp:
        json.dump(content, fp, indent=4)

write_json("../output/characteristics/validation/online_sites.json", list(online_sites))
write_json("../output/characteristics/validation/offline_sites.json", list(offline_sites))



# Extract only the IPs of offline websites
offline_domains_to_check = {}
for domain in offline_sites:
    if domain in domain_ip_mapping:
        offline_domains_to_check[domain] = domain_ip_mapping[domain]  # Store all IPs for the domain

write_json("../output/characteristics/validation/offline_domain_ips.json", offline_domains_to_check)
