## 🔗 Quick Links

- ![CH](https://img.shields.io/badge/CH-Switzerland-red) [Switzerland Critical Prefixes](https://github.com/kastanakis/critical-bgp-prefixes/blob/main/critical_prefixes/output/hardenize_parsed/prefixes_per_country/ch-resilience_domain2pfx_routeviews.json)
- ![EE](https://img.shields.io/badge/EE-Estonia-blue) [Estonia Critical Prefixes](https://github.com/kastanakis/critical-bgp-prefixes/blob/main/critical_prefixes/output/hardenize_parsed/prefixes_per_country/ee-tld_domain2pfx_routeviews.json)
- ![LT](https://img.shields.io/badge/LT-Lithuania-green) [Lithuania Critical Prefixes](https://github.com/kastanakis/critical-bgp-prefixes/blob/main/critical_prefixes/output/hardenize_parsed/prefixes_per_country/lithuania-dashboard_domain2pfx_routeviews.json)
- ![SE](https://img.shields.io/badge/SE-Sweden-yellow) [Sweden Critical Prefixes](https://github.com/kastanakis/critical-bgp-prefixes/blob/main/critical_prefixes/output/hardenize_parsed/prefixes_per_country/sweden-health-status_domain2pfx_routeviews.json)
- ![NL](https://img.shields.io/badge/NL-Netherlands-orange) [Netherlands Critical Prefixes](https://github.com/kastanakis/critical-bgp-prefixes/blob/main/critical_prefixes/output/basisbeveiliging_parsed/domain2pfx_merged.json)

---

# Critical BGP Prefixes

Measurement framework and datasets for identifying and analyzing BGP prefixes that host publicly reachable Critical Infrastructure (CI) services.

This repository accompanies the IFIP Networking 2026 workshop paper **Critical BGP Prefixes: A Measurement-based Investigation of Critical Infrastructure Security**, presented at the **4th IOCRCI Workshop: Impact of IT/OT Convergence on the Resilience of Critical Infrastructures**.

The project studies the Internet routing infrastructure behind publicly reachable government, healthcare, educational, financial, and other critical services across multiple countries.

---

# Abstract

Critical Infrastructure (CI) organizations increasingly depend on Internet-routed services to provide essential public functionality. Despite their societal importance, little is known about the BGP prefixes and Autonomous Systems (ASes) that host these services.

This repository provides the datasets, measurement scripts, and analysis pipeline used to:

* identify prefixes hosting CI services
* infer originating ASes
* evaluate routing-security properties
* analyze resilience and visibility
* measure outages and hijack exposure
* characterize geographical deployment patterns

The framework combines Internet topology analysis, routing-security measurements, and operational validation into a reproducible Internet-scale measurement pipeline.

---

# Repository Structure

```text
.
├── anycast-census/        # Anycast Census datasets
├── asdb/                  # ASN business-sector classification datasets
├── basisbeveiliging/      # Dutch CI datasets and domain collections
├── bgptools/              # External anycast prefix datasets
├── caida/                 # CAIDA topology and AS relationship datasets
├── critical_prefixes/
│   ├── characteristics/   # Core analysis and plotting scripts
│   ├── domain2pfx/        # Domain → IP → Prefix translation pipeline
│   └── output/            # Generated outputs and intermediate artifacts
├── cymru/                 # Bogon filtering datasets
├── hardenize/             # International CI domain collections
└── rovista/               # ROV deployment datasets
```

---

# Measurement Pipeline

The framework follows the pipeline below:

```text
Critical Infrastructure Domains
            ↓
      DNS Resolution
            ↓
        IP Collection
            ↓
     Prefix Inference
            ↓
        ASN Mapping
            ↓
 Business/Sector Mapping
            ↓
 Routing & Security Analysis
```

The resulting datasets are then used for:

* RPKI analysis
* ROV analysis
* routing visibility measurements
* outage analysis
* hijack analysis
* geolocation analysis
* resilience estimation
* anycast characterization
* operational validation

---

# Data Sources

| Source         | Purpose                       |
| -------------- | ----------------------------- |
| CAIDA          | AS relationships and topology |
| RouteViews     | Prefix-to-AS mappings         |
| RIPEstat       | RPKI, visibility, geolocation |
| RoVista        | ROV deployment                |
| IODA           | Internet outage events        |
| GRIP           | Hijack events                 |
| Anycast Census | Anycast detection             |
| BGP.Tools      | Anycast prefix datasets       |
| Team Cymru     | Bogon filtering               |
| Hardenize      | Domain collections            |
| ASdb           | ASN business classification   |
| Tranco         | Popularity rankings           |

---

# Installation

Recommended environment:

* Python 3.10+
* Linux-based OS

Install dependencies:

```bash
pip install requests tqdm matplotlib numpy pandas aiohttp plotly pillow pycountry ijson kaleido
```

---

# Output Artifacts

Generated outputs are stored under:

```text
critical_prefixes/output/
```

Example outputs include:

* RPKI validation datasets
* ROV coverage measurements
* outage statistics
* hijack measurements
* visibility CDFs
* geolocation maps
* resilience plots
* business-sector distributions

---

# License

See the included `LICENSE` file.

---

# Acknowledgements

This work relies on publicly available datasets and APIs provided by:

* CAIDA
* RIPE NCC
* RouteViews
* IODA
* Georgia Tech Internet Intelligence Lab
* RoVista
* Team Cymru
* Hardenize
* Tranco

Their public infrastructure and datasets make Internet measurement research possible.
