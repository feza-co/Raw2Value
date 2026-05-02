# Hackathon Rule Compliance - PomzaScope

Source: `HACKATHON_KURALLARI.md`

## Theme Fit

PomzaScope is positioned under **Akilli Tedarik Zinciri Sistemleri**.

- Module A: satellite + AI detects pumice extraction sites and growth.
- Module B / demo page: pumice hauling route, CO2, and currency-linked carbon cost.
- Cave2Cloud story: local Nevsehir pumice producers get a cloud dashboard for site
  visibility, compliance, and export/transport decisions.

## Mandatory Rule 1 - Geographic Carbon Footprint

Implemented in:

- `code/p5/11_cave2cloud_rules.py`
- `code/p5/dashboard.py` page `4) Cave2Cloud Uyumu`

Logic:

1. User enters origin/destination coordinates and tonnage.
2. OSRM public demo server over OpenStreetMap calculates route distance dynamically.
3. CO2 is calculated as:

```text
CO2 kg = distance_km * tonnage * emission_factor
```

Emission factors are the rule-table factors:

| Mode | kg CO2 / ton-km |
|---|---:|
| road | 0.100 |
| rail | 0.030 |
| sea | 0.015 |
| air | 0.500 |

No route distance is hardcoded.

## Mandatory Rule 2 - Live TCMB EVDS FX

Implemented in:

- `code/p5/11_cave2cloud_rules.py`
- `code/p5/dashboard.py` page `4) Cave2Cloud Uyumu`

The code uses TCMB EVDS endpoint:

```text
https://evds2.tcmb.gov.tr/service/evds/
```

Supported pairs:

- `USD/TRY` -> `TP.DK.USD.A.YTL`
- `EUR/TRY` -> `TP.DK.EUR.A.YTL`

Required environment variable:

```powershell
$env:TCMB_EVDS_API_KEY="..."
```

If the key is missing, the dashboard shows a red warning and does **not** use a
hardcoded exchange rate. This is intentional: missing EVDS key is visible to the
jury instead of silently violating the rule.

## Mandatory Rule 3 - Independent Geographic Operation

Implemented independently of the carbon calculation:

- OSRM route distance and duration are displayed as their own operational
  logistics output.
- Module A also performs geospatial filtering/overlay:
  - AOI bbox and raster alignment in EPSG:32636.
  - OSM/WHC Goreme protected area buffer overlay.
  - Positive/negative pixel sampling by spatial masks.

For the presentation, use the route distance/duration KPI in the Cave2Cloud page
as the cleanest Rule 3 demonstration.

## Current Compliance Risks

| Risk | Status | Action |
|---|---|---|
| TCMB EVDS key missing | Open | Set `TCMB_EVDS_API_KEY` before demo. |
| Agriculture mask not downloaded yet | Non-blocking | ESA WorldCover GEE task `MEA2PS6722KFTWJXVZWM5443` is running/ready in Drive. |
| S1 change layer missing | Non-blocking | Current S1 data is a seasonal composite, not two timestamped S1 scenes. Leave layer off or show placeholder. |
| ASTER coverage only ~19.9% on extended AOI | Accepted Plan B | Dashboard can use P3 raw + partial P4 fuse; mention ASTER scene coverage limitation. |

## Demo Script Fit

1. Open dashboard.
2. Show detected pumice area and UNESCO buffer.
3. Open `Cave2Cloud Uyumu`.
4. Enter one pumice site and one factory/Avanos destination.
5. Press `Dinamik hesapla`.
6. Explain:
   - OSRM/OpenStreetMap distance is dynamic.
   - CO2 uses the provided rule-table factors.
   - TCMB EVDS rate drives TL carbon cost when key is configured.
