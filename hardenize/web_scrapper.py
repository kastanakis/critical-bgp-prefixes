import requests
from bs4 import BeautifulSoup
import json
from pprint import pprint as pprint

def write_json(jsonfilename, content):
    with open(jsonfilename, 'w') as fp:
        json.dump(content, fp, indent=4)

def get_hostnames(url):
    # Step 1: Fetch the webpage source
    response = requests.get(url)

    if response.status_code == 200:
        print("Page fetched successfully!")
        
        # Step 2: Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Step 3: Find the element with id="jsondata"
        json_element = soup.find(id="jsonData")
        
        if json_element:
            json_text = json_element['jsondata']  # Extract the text content of the element
            try:
                # Step 4: Parse the extracted text as JSON and return the respective domains
                json_data = json.loads(json_text)
                return list({elem['hostname'] for elem in json_data})
            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)
        else:
            print("No element found with id='jsondata'.")
    else:
        print(f"Failed to fetch the page. HTTP Status Code: {response.status_code}")


if __name__ == '__main__':
    urls = ["https://www.hardenize.com/dashboards/ch-resilience/",\
            "https://www.hardenize.com/dashboards/do-resilience/",\
             "https://www.hardenize.com/dashboards/ee-tld/",\
             "https://www.hardenize.com/dashboards/hu-resilience/",\
             "https://www.hardenize.com/dashboards/lithuania-dashboard/",\
             "https://www.hardenize.com/dashboards/sweden-health-status/",\
             "https://www.hardenize.com/dashboards/bahamas-web-hygiene-dashboard/",\
             "https://www.hardenize.com/dashboards/global-top-sites/"]
    
    for url in urls: 
        name = url.split("dashboards/")[1].strip("/")
        domains = get_hostnames(url)
        if domains:
            print((name, len(domains)))
            write_json("critical_domains_" + name + ".json", domains)