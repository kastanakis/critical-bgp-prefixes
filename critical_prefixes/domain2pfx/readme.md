0. First preprocess the data and extract the basisbeveiliging or tranco domains.

1. Resolve domain to IPs.

Basisbeveliging

IPv4 addresses:
../../massdns-master/bin/massdns -r ../../massdns-master/lists/resolvers.txt -t A -o S ../output/basisbeveiliging_parsed/all_basibeveiligin_domains.csv > ../output/basisbeveiliging_parsed/all_basisbeveiliging_ipv4.txt 

IPv6 addresses:
../../massdns-master/bin/massdns -r ../../massdns-master/lists/resolvers.txt -t AAAA -o S ../output/basisbeveiliging_parsed/all_basibeveiligin_domains.csv > ../output/basisbeveiliging_parsed/all_basisbeveiliging_ipv6.txt


Tranco

IPv4 addresses:
../../massdns-master/bin/massdns -r ../../massdns-master/lists/resolvers.txt -t A -o S ../output/tranco_parsed/all_tranco_domains.csv > ../output/tranco_parsed/all_tranco_ipv4.txt

IPv6 addresses:
../../massdns-master/bin/massdns -r ../../massdns-master/lists/resolvers.txt -t AAAA -o S ../output/tranco_parsed/all_tranco_domains.csv > ../output/tranco_parsed/all_tranco_ipv6.txt


Hardenize
IPv4 addresses:
../../massdns-master/bin/massdns -r ../../massdns-master/lists/resolvers.txt -t A -o S ../output/hardenize_parsed/domains_per_country/bahamas-web-hygiene-dashboard_domains.csv > ../output/hardenize_parsed/domains_per_country/bahamas-web-hygiene-dashboard_ipv4.txt
../../massdns-master/bin/massdns -r ../../massdns-master/lists/resolvers.txt -t A -o S ../output/hardenize_parsed/domains_per_country/ch-resilience_domains.csv > ../output/hardenize_parsed/domains_per_country/ch-resilience_ipv4.txt
../../massdns-master/bin/massdns -r ../../massdns-master/lists/resolvers.txt -t A -o S ../output/hardenize_parsed/domains_per_country/ee-tld_domains.csv > ../output/hardenize_parsed/domains_per_country/ee-tld_ipv4.txt
../../massdns-master/bin/massdns -r ../../massdns-master/lists/resolvers.txt -t A -o S ../output/hardenize_parsed/domains_per_country/global-top-sites_domains.csv > ../output/hardenize_parsed/domains_per_country/global-top-sites_ipv4.txt
../../massdns-master/bin/massdns -r ../../massdns-master/lists/resolvers.txt -t A -o S ../output/hardenize_parsed/domains_per_country/lithuania-dashboard_domains.csv > ../output/hardenize_parsed/domains_per_country/lithuania-dashboard_ipv4.txt
../../massdns-master/bin/massdns -r ../../massdns-master/lists/resolvers.txt -t A -o S ../output/hardenize_parsed/domains_per_country/sweden-health-status_domains.csv > ../output/hardenize_parsed/domains_per_country/sweden-health-status_ipv4.txt

IPv6 addresses:
../../massdns-master/bin/massdns -r ../../massdns-master/lists/resolvers.txt -t AAAA -o S ../output/hardenize_parsed/domains_per_country/bahamas-web-hygiene-dashboard_domains.csv > ../output/hardenize_parsed/domains_per_country/bahamas-web-hygiene-dashboard_ipv6.txt
../../massdns-master/bin/massdns -r ../../massdns-master/lists/resolvers.txt -t AAAA -o S ../output/hardenize_parsed/domains_per_country/ch-resilience_domains.csv > ../output/hardenize_parsed/domains_per_country/ch-resilience_ipv6.txt
../../massdns-master/bin/massdns -r ../../massdns-master/lists/resolvers.txt -t AAAA -o S ../output/hardenize_parsed/domains_per_country/ee-tld_domains.csv > ../output/hardenize_parsed/domains_per_country/ee-tld_ipv6.txt
../../massdns-master/bin/massdns -r ../../massdns-master/lists/resolvers.txt -t AAAA -o S ../output/hardenize_parsed/domains_per_country/global-top-sites_domains.csv > ../output/hardenize_parsed/domains_per_country/global-top-sites_ipv6.txt
../../massdns-master/bin/massdns -r ../../massdns-master/lists/resolvers.txt -t AAAA -o S ../output/hardenize_parsed/domains_per_country/lithuania-dashboard_domains.csv > ../output/hardenize_parsed/domains_per_country/lithuania-dashboard_ipv6.txt
../../massdns-master/bin/massdns -r ../../massdns-master/lists/resolvers.txt -t AAAA -o S ../output/hardenize_parsed/domains_per_country/sweden-health-status_domains.csv > ../output/hardenize_parsed/domains_per_country/sweden-health-status_ipv6.txt

2. Group IPs per domain. Specify Tranco, Hardenize or Basisbeveiliging.

3. Translate for each domain each IP to the respective prefix through RIPEStat or Routeviews. For Tranco and Hardenize we will be using only Routeviews. The output is grouped IP prefixes per domain.

4. For basisbeveiliging we are using RIPE and RV, hence, we need to merge the produced datasets. For tranco we dont diff_and_merge.py.

4. We can also reduce an IP to the respective ASn with RipeStat and have grouped ASns per domain.