# Nigeria Domestic Flight Delay Tracker

An open, cleaned dataset and dashboard built from the Nigerian Civil Aviation Authority (NCAA) monthly *Summary of Domestic Airline Flight Disruption Operations*, with a roadmap toward flight-level delay prediction.

**Author:** Eric Allagoa | B.Sc. Computer Science (A.I. and Machine Learning), American University of Nigeria | eric.allagoa5@gmail.com

**Status:** the cleaned dataset is published. The dashboard is in progress.

## Why this project exists

Delays are one of the most persistent problems in Nigerian domestic aviation, but the public data is scattered across monthly reports. I could not find an open, structured version of it. This project turns the NCAA's published figures into a clean dataset and a dashboard so that airline performance can be compared over time.

## Stage 1 (this repository): NCAA monthly data

- Collect each monthly NCAA disruption summary and record it in one tidy CSV.
- Compute delay rate and cancellation rate per airline per month.
- Publish a dashboard: airline rankings, monthly trends, delay-length breakdown (in progress).

### Data dictionary (`data/ncaa_disruptions.csv`)

One row per airline per period (plus an `ALL AIRLINES` row for network totals).

| Column | Description |
|---|---|
| `period` | Reporting period start (YYYY-MM). For a quarter, the first month of the quarter |
| `period_type` | `month` or `quarter` |
| `airline` | Airline name (spelling standardised across documents) |
| `total_flights` | Flights operated. Empty where a source gives no per-airline monthly figure |
| `delayed_over_15min` | Flights delayed more than 15 minutes. Only the monthly summary (August 2026) reports this |
| `delayed_over_1h` | Flights delayed more than 1 hour. Reported by the quarterly summaries; for August it is the sum of the 1-2h, 2-3h and 3h+ buckets |
| `delayed_16_60min`, `delayed_1_2h`, `delayed_2_3h`, `delayed_3h_plus` | Delay-length buckets (August 2026 only) |
| `cancelled_flights` | Flights cancelled |
| `passengers`, `passengers_affected` | Passenger counts, where the source gives them |
| `source_doc` | Name of the NCAA document |
| `source_url` | Where the document or a report on it can be found |
| `notes` | Anything disputed, inconsistent or unclear in the source |

**Compare like with like:** the quarterly executive summaries count only delays above one hour, while the August monthly summary counts delays from 16 minutes. Use `delayed_over_1h` when comparing across documents. Never compare `delayed_over_15min` with the quarterly figures.

## Limitations (read before using the data)

- The NCAA publishes **airline-level monthly totals**, not flight-by-flight records, so this stage cannot support a flight-level predictor.
- Airlines have publicly disputed the NCAA's figures and how causes of delay are attributed. Treat the numbers as the regulator's published data, not as verified ground truth.
- The NCAA's documents use different definitions of "delayed" (see above). Always check the definition before comparing periods.
- Some source tables are internally inconsistent (for example, the Q2 2026 summary table's airline flight counts do not add up to its stated total). These are corrected where the document itself shows which figure reconciles, and flagged in `notes`.
- Reports differ in format across months, so some fields may be missing for some airlines.

## Roadmap

1. **Stage 1:** NCAA monthly dataset and dashboard (this repo).
2. **Stage 2:** Build a flight-level log (scheduled vs. actual times, plus weather) for a small set of routes, using only sources whose terms allow it.
3. **Stage 3:** Train a baseline model to predict a delay of more than 15 minutes. Because roughly six in ten flights were delayed in recent months, a "predict delayed every time" baseline is already about 60% accurate, so results are reported with AUC and F1 and compared against that baseline.

## How to run (coming once the dashboard is built)

```bash
pip install pandas matplotlib plotly streamlit
streamlit run app.py
```

## Tools

Python, pandas, Plotly, Streamlit (free hosting on Streamlit Community Cloud).

## Data sources and credit

The original NCAA documents are kept in `data/raw/` so every figure can be checked against its source.

Figures come from NCAA published reports and news coverage of them. Each row carries its `source_url`. This project is independent and is not affiliated with the NCAA or any airline.

## Licence

Code: MIT. Data: cite the NCAA as the original source.
