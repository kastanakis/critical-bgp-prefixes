import json
import asyncio
import subprocess
from tqdm.asyncio import tqdm
import itertools

# -------------------------------
# PING & TCP CHECK FOR OFFLINE IPS
# -------------------------------

# Reads content of JSON file and returns
def read_json(jsonfilename):
    with open(jsonfilename, 'r') as jsonfile:
        return json.load(jsonfile)

# Save online & offline sites
def write_json(jsonfilename, content):
    with open(jsonfilename, 'w') as fp:
        json.dump(content, fp, indent=4)

# Returns a flat list from a list of lists
def flatten_list(lista):
    return list(itertools.chain.from_iterable(lista))

online_sites = read_json("../output/characteristics/validation/online_sites.json")
offline_sites = read_json("../output/characteristics/validation/offline_sites.json")
offline_domains_to_check = read_json("../output/characteristics/validation/offline_domain_ips.json")

print(f"\nOnline Websites: {len(online_sites)}")
print(f"Offline Websites (Before IP Check): {len(offline_sites)}")
print(f"Extracted {len(offline_domains_to_check)} offline websites with {len(flatten_list(offline_domains_to_check.values()))} IPs for deeper analysis.")

# Async function to ping an IP using ICMP
async def ping_ip(ip, semaphore):
    async with semaphore:
        try:
            result = await asyncio.to_thread(subprocess.run, ["ping", "-c", "1", "-W", "1", ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return ip, result.returncode == 0  # 0 = online, otherwise offline
        except Exception:
            return ip, False  # Assume offline on error

# Async function to check TCP connection (fallback)
async def tcp_ping(ip, port, semaphore):
    async with semaphore:
        try:
            reader, writer = await asyncio.open_connection(ip, port, limit=1_000_000)
            writer.close()
            await writer.wait_closed()
            return ip, True  # IP is online
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            return ip, False  # IP is offline

# Combined async function: Try ICMP, then TCP if ICMP fails
async def check_ip(ip, semaphore):
    """First try ICMP ping, if it fails, try TCP SYN."""
    ip, is_online = await ping_ip(ip, semaphore)
    if not is_online:  # If ICMP fails, try TCP
        ip, is_online = await tcp_ping(ip, 443, semaphore)
    return ip, is_online

# Main async function with a real-time progress bar
async def check_all_ips():
    semaphore = asyncio.Semaphore(500)  # Create semaphore inside function
    ip_tasks = []
    domain_ip_mapping = {}  # Map domain -> list of tasks for its IPs

    # Create tasks for each domain's IP
    for domain, ip_list in offline_domains_to_check.items():
        domain_ip_mapping[domain] = []
        for ip in ip_list:
            task = asyncio.create_task(check_ip(ip, semaphore))  # ✅ Create an actual Task
            ip_tasks.append(task)
            domain_ip_mapping[domain].append((ip, task))  # Store (IP, task) for tracking

    # Process results with tqdm progress bar
    results = []
    for future in tqdm(asyncio.as_completed(ip_tasks), total=len(ip_tasks), desc="Checking Offline IPs", ncols=80):
        ip, is_online = await future
        results.append((ip, is_online))

    # Rebuild domain -> IP status mapping
    domain_status = {}
    for domain, ip_task_list in domain_ip_mapping.items():
        domain_status[domain] = [is_online for ip, task in ip_task_list if (ip, is_online) in results]

    return domain_status

# Run the async IP checker
domain_status = asyncio.run(check_all_ips())

# Determine final domain status
final_online_sites = {domain for domain, ip_statuses in domain_status.items() if any(ip_statuses)}
final_offline_sites = {domain for domain, ip_statuses in domain_status.items() if all(not status for status in ip_statuses)}

write_json("../output/characteristics/validation/final_online_sites.json", list(final_online_sites))
write_json("../output/characteristics/validation/final_offline_sites.json", list(final_offline_sites))

print(f"\nFinal Online Websites: {len(final_online_sites)}")
print(f"Final Offline Websites: {len(final_offline_sites)}")