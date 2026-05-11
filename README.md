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

# Included Datasets

The repository aggregates publicly reachable Critical Infrastructure datasets from multiple countries and sectors.

## Countries Included

* Netherlands
* Switzerland
* Estonia
* Lithuania
* Sweden

## Critical Infrastructure Sectors

Examples include:

* Government
* Healthcare
* Education
* Finance
* Energy
* Municipal services
* Cybersecurity organizations
* Public administration

---

# Core Components

## Domain Collection

The repository includes curated CI domain collections derived from:

* national datasets
* Hardenize dashboards
* governmental registries
* public infrastructure inventories

The datasets are normalized and filtered to obtain publicly reachable domains.

---

## Domain → Prefix Translation

The `domain2pfx/` subsystem performs:

```text
Domain
  ↓
DNS Resolution
  ↓
IP Address Collection
  ↓
Prefix Mapping
  ↓
ASN Inference
```

Outputs include:

* `domain2ip.json`
* `domain2pfx.json`
* `domain2asn.json`

---

## Internet Topology Analysis

The repository integrates CAIDA datasets for:

* AS relationship analysis
* customer-cone inference
* provider diversity analysis
* AS organization mapping
* resilience estimation

Included datasets:

* CAIDA AS relationships
* RouteViews prefix-to-AS mappings
* customer-cone datasets
* AS organization datasets

---

## Routing Security Analysis

The framework evaluates routing-security properties using:

* RIPEstat APIs
* RoVista datasets

### Measurements

* RPKI validation
* Route Origin Validation (ROV)
* routing visibility
* prefix propagation

The repository measures:

* valid prefixes
* invalid prefixes
* unknown prefixes
* ROV deployment ratios
* visibility distributions

and compares them against random public prefixes and ASes.

---

## Anycast Analysis

The repository integrates:

* Anycast Census datasets
* BGP.Tools anycast lists

to identify:

* anycasted CI prefixes
* geographically distributed deployments
* resilient hosting infrastructures

---

## Outage Analysis

Outage measurements are collected using:

* IODA APIs

The framework analyzes:

* outage counts
* outage durations
* country-specific outage exposure
* comparisons against random AS populations

---

## Hijack Analysis

The repository measures BGP hijack exposure using:

* GRIP (Georgia Tech)

The framework evaluates:

* MOAS events
* suspicious routing anomalies
* hijack durations
* ASN-level exposure

---

## Geolocation Analysis

Prefix geolocation is performed using:

* RIPEstat geolocation APIs
* MaxMind GeoLite data

The repository analyzes:

* hosting concentration
* foreign hosting dependencies
* geographic distribution
* infrastructure centralization

---

## Business Classification

ASNs are mapped into business sectors using:

* ASdb datasets

Example sectors include:

* Government and Public Administration
* Finance and Insurance
* Healthcare
* Education and Research
* Utilities
* Hosting Providers
* Telecommunications

---

## Operational Validation

The repository validates operational reachability using:

* HTTP probing
* ICMP probing
* TCP fallback validation

This ensures that measured services are:

* active
* reachable
* publicly deployed

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

# Example Workflow

## Translate domains to prefixes

```bash
python translate_ip_to_prefix_routeviews.py
```

## Collect RPKI measurements

```bash
python collect_rpki_per_prefix.py
```

## Collect visibility measurements

```bash
python collect_visibility_per_prefix.py
```

## Collect outage data

```bash
python collect_outages.py
```

## Generate plots

```bash
python plot_rpki.py
python plot_visibility.py
python plot_rov_coverage.py
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

# Reproducibility Notes

This repository is designed as a reproducible research artifact.

However, results may vary over time due to:

* evolving BGP routing conditions
* updated CAIDA snapshots
* changing RPKI/ROV deployment
* API data freshness
* changing Internet topology

Dataset timestamps are preserved whenever possible.

---

# Ethical Considerations

This repository exclusively uses:

* publicly accessible datasets
* publicly reachable services
* passive Internet measurements
* publicly documented APIs

The framework is intended for:

* academic research
* resilience analysis
* routing-security studies
* Critical Infrastructure analysis

No active exploitation or intrusive measurements are performed.

---

# Citation

If you use this repository, datasets, or methodology in academic work, please cite the associated paper.

```bibtex
@misc{criticalbgpprefixes,
  title={Critical BGP Prefixes: Characterizing the Routing Infrastructure of Public Critical Services},
  author={Authors},
  year={2025}
}
```

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
