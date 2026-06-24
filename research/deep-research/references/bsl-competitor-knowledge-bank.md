# BSL Competitor Knowledge Bank

Condensed reference for future BSL competitive research. Compiled June 2026.

## BSL Profile (from brendamourlogistics.com)

- **HQ:** 2630 Glendale Milford Road, Cincinnati, OH 45241
- **Phone:** 800-354-9715 Ext. 110
- **Founded:** 1983 (as Brendamour Moving & Storage); kiosk logistics since ~2005
- **Ownership:** Family-operated (Brendamour family)
- **Warehousing:** 1M+ sq ft in Cincinnati; national service partner network
- **Scale:** 70,000+ Redbox units installed; nearly all retail Amazon Lockers; 10,000+ installs/year since 2005
- **Service Partners:** National network est. 2017; 2,500+ installs/year; in-person trained
- **Site Surveys:** 50,000+ completed in 3 years
- **Repair Depot:** In-house, shared with vendor partner
- **Website CMS:** CMSMax (not WordPress) — assets served from `media.cmsmax.cloud`
- **Website gap:** Markets exclusively as "Turnkey Kiosk Logistics" — vending, ATM, EV charging verticals NOT on website despite being served

## Key Competitors (by category)

### Multi-Vertical (closest to BSL)
| Competitor | HQ | Verticals | Notes |
|------------|-----|-----------|-------|
| **TecDis (Rhenus Group)** | Germany | Vending, gaming, ATM, kiosk, IT, medical, data center | Europe-only. Control tower + specialist partner network. Est. 2008. Closest model to BSL worldwide. Monitor for US entry. |
| **Burroughs** | Plymouth, MI | Payment/ATM, unattended self-service, IoT, robotics | Full lifecycle: remote monitoring, dispatch, help desk, parts logistics, depot repair. Technology leader in field services. |

### Vending Logistics
| Competitor | HQ | Notes |
|------------|-----|-------|
| Canteen (Compass Group) | Charlotte, NC | Nation's largest vending operator. In-house logistics — captive, not a 3PL. |
| Vistar (PFG) | Denver, CO | Vending product distributor. Not equipment installer. |

### Parcel Lockers
| Competitor | HQ | Notes |
|------------|-----|-------|
| Luxer One | Sacramento, CA | Locker OEM. Multifamily, retail, office, university. |
| Quadient (Parcel Pending) | France (US ops) | Locker OEM + mail automation. |
| Package Concierge | US | Locker OEM. |
| Amazon Locker | Seattle, WA | BSL is their installation partner — nearly all retail Amazon Lockers. |

### ATM
| Competitor | HQ | Notes |
|------------|-----|-------|
| NCR Atleos | Atlanta, GA | ATM OEM + service. NYSE: NATL. |
| Diebold Nixdorf | North Canton, OH | ATM + retail tech OEM. **Ohio-based — 4 hrs from Cincinnati.** Potential partner. |
| Brink's | Richmond, VA | Cash logistics/CIT. Not equipment installer. |
| Loomis | Houston, TX | Cash management + technology. |

### EV Charging
| Competitor | HQ | Notes |
|------------|-----|-------|
| Blink Charging | Bowie, MD | Vertically integrated EV network. NASDAQ: BLNK. Has installer resources, Blink Academy, commissioning, grants support. Potential customer/partner. |
| ChargePoint | Campbell, CA | EV network operator. ChargePoint University. Partners with installers. Potential customer/partner. |
| EVgo | Los Angeles, CA | DCFC network. |
| Electrify America | Reston, VA | DCFC highway network. VW settlement-funded. |
| Wesco / Graybar / Sonepar | Pittsburgh / St. Louis / Paris | Electrical distributors — supply channel, not competitors. |

### Kiosk Manufacturing
| Competitor | HQ | Notes |
|------------|-----|-------|
| Frank Mayer | Grafton, WI | Custom kiosk + retail display manufacturer. Midwest-based. In-house design. |
| Meridian Kiosks | Aberdeen, NC | Kiosk OEM + Mzero software (remote monitoring, analytics). ISO 9001:2015, UL certified. 13-acre campus. |
| Olea Kiosks | Los Angeles, CA | Kiosk OEM. 50+ years, Made in USA. Standard + custom. |

### Combined Warehousing + Installation (Last Mile)
| Competitor | HQ | Notes |
|------------|-----|-------|
| Fidelitone | Wauconda, IL | 90 years. Last mile + white glove + warehousing. Consumer goods (health, beauty, mattress, MRO). Midwest-based. |
| McCollister's | Burlington, NJ | 75+ years. Specialized transportation & logistics. JS-heavy site. |
| J.B. Hunt Final Mile | Lowell, AR | Asset-based 3PL. Consumer goods final mile. |
| XPO Last Mile | Greenwich, CT | Asset-based 3PL. Consumer goods. |
| BlueGrace | Tampa, FL | 3PL brokerage (non-asset). White glove, light assembly. |
| SEKO Logistics | Itasca, IL | Global freight forwarding. Midwest presence. Generalist. |

## Market Data (June 2026)

| Vertical | Market Size | Growth | Source |
|----------|------------|--------|--------|
| US Vending Machines | $21.9B (2024) → $30.27B (2033) | 3.66% CAGR | ResearchAndMarkets |
| Smart Parcel Lockers (NA) | Double-digit growth | ~12-15% CAGR est. | Ken Research, Verified Market Research |
| Global ATM | Declining in developed markets | 9.2% CAGR (India) | Expert Market Research, Mordor Intelligence |
| Ultra-Fast EV Charging | $2.18B (2024) → $14.81B (2034) | 20.1% CAGR | GM Insights |
| White Glove Last Mile | → $52.7B (2030) | 11.7% CAGR | Verified Market Research |
| NEVI Program | $5B+ federal funding | — | Environment America, state-level reports |

## Search Techniques That Worked

- **Marginalia Search:** `https://old-search.marginalia.nu/search?query={QUERY}` — effective but rate-limited after 3-4 rapid queries. Space queries 8+ seconds apart.
- **Direct competitor site fetches:** `curl -sL --max-time 15 -H 'User-Agent: Mozilla/5.0 (compatible; research)' '{URL}'` — works for most sites. JS-rendered sites return minimal text; extract title + meta description + strip tags.
- **CMSMax detection:** Assets from `media.cmsmax.cloud` indicate CMSMax, not WordPress. WP REST API won't work.
- **Market data:** Marginalia surfaced market research report pages (ResearchAndMarkets, Mordor Intelligence, GM Insights, Verified Market Research, Persistence Market Research) with specific dollar figures and CAGRs.
