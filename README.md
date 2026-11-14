# Nigeria Domestic Flight Delay Tracker

An open, cleaned dataset and dashboard built from the Nigerian Civil Aviation Authority (NCAA) monthly *Summary of Domestic Airline Flight Disruption Operations*, with a roadmap toward flight-level delay prediction.

**Author:** Eric Allagoa | B.Sc. Computer Science (A.I. and Machine Learning), American University of Nigeria | eric.allagoa5@gmail.com

## Why this project exists

Delays are one of the most persistent problems in Nigerian domestic aviation, but the public data is scattered across monthly reports. I could not find an open, structured version of it. This project turns the NCAA's published figures into a clean dataset and a dashboard so that airline performance can be compared over time.

## Stage 1 (this repository): NCAA monthly data

- Collect each monthly NCAA disruption summary and record it in one tidy CSV.
- Compute delay rate and cancellation rate per airline per month.
- Publish a dashboard: airline rankings, monthly trends, delay-length breakdown.

### Data dictionary (`data/ncaa_disruptions.csv`)

| Column | Description |
|---|---|
| `period` | Reporting period start (YYYY-MM) |
| `period_type` | `month`, `quarter` or `year`, depending on the NCAA document |
| `airline` | Airline name as published by the NCAA |
| `total_flights` | Flights operated |
| `delayed_flights` | Flights recorded as delayed |
| `cancelled_flights` | Flights cancelled |
| `delay_16_60min`, `delay_1_2h`, `delay_2_3h`, `delay_3h_plus` | Delay-length buckets, where the report provides them |
| `delay_rate` | `delayed_flights / total_flights` (derived) |
| `cancel_rate` | `cancelled_flights / total_flights` (derived) |
| `source_url` | Link to the NCAA publication or news report the figures came from |
| `notes` | Anything disputed or unclear (for example, an airline contesting the figures) |

Fill in only what each report actually states. Leave a cell empty if a report does not provide it.

## Limitations (read before using the data)

- The NCAA publishes **airline-level monthly totals**, not flight-by-flight records, so this stage cannot support a flight-level predictor.
- Airlines have publicly disputed the NCAA's figures and how causes of delay are attributed. Treat the numbers as the regulator's published data, not as verified ground truth.
- Check the NCAA's definition of "delayed" in each report before comparing months. The report buckets suggest delays start above 15 minutes, but confirm this from the source document.
- Reports differ in format across months, so some fields may be missing for some airlines.

## Roadmap

1. **Stage 1:** NCAA monthly dataset and dashboard (this repo).
2. **Stage 2:** Build a flight-level log (scheduled vs. actual times, plus weather) for a small set of routes, using only sources whose terms allow it.
3. **Stage 3:** Train a baseline model to predict a delay of more than 15 minutes. Because roughly six in ten flights were delayed in recent months, a "predict delayed every time" baseline is already about 60% accurate, so results are reported with AUC and F1 and compared against that baseline.

## How to run

```bash
pip install pandas matplotlib plotly streamlit
streamlit run app.py
```

## Tools

Python, pandas, Plotly, Streamlit (free hosting on Streamlit Community Cloud).

## Data sources and credit

Figures come from NCAA published reports and news coverage of them. Each row carries its `source_url`. This project is independent and is not affiliated with the NCAA or any airline.

## Licence

Code: MIT. Data: cite the NCAA as the original source.
