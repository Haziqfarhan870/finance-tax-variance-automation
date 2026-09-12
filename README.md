# Finance Tax Variance Automation — Portfolio Reimplementation

A Python/pandas portfolio project showing how a recurring tax-variance review can turn ERP-style P&L and balance-sheet extracts into quarterly analysis, materiality alerts, deterministic variance commentary, reviewer status tracking, and management summary sheets.

> **Important:** this is a portfolio reimplementation inspired by a finance automation workflow I developed during an internship. It uses entirely synthetic data, fictional entities, fictional account codes, and generalized business rules. The original employer's data, mappings, source code, report names, thresholds, and internal processes are not reproduced.

## Business problem

Quarterly tax review can require finance teams to combine GL line-item files across legal entities and periods, distinguish P&L activity from balance-sheet closing balances, identify material movements, understand the transactions behind those movements, and track review completion.

In the original internship workflow, automation reduced quarterly variance-analysis turnaround by approximately **75%**. That figure describes the original business process; it is **not** a benchmark of this synthetic demo.

## What this public repo demonstrates

- **Multi-period ERP-style ingestion** using year folders and quarterly files.
- **Column normalization** for inconsistent export headers such as `Pstng Date`, `G/L Account`, `Comp. Code`, and equivalent variants.
- **Data quality controls** that remove subtotal/spacer rows, coerce dates and amounts, and remove only exact duplicate rows.
- **Configurable account mapping** with explicit detection of new/unmapped accounts.
- **Different accounting treatment for P&L and balance sheet:**
  - P&L uses quarter activity and current-year YTD accumulation.
  - Balance sheet uses quarter-end Trial Balance closing balances when available; a cumulative GL fallback is available if TB data is absent.
- **Quarter-over-quarter metrics:** delta, percentage change, YTD, direction indicator, and materiality flagging.
- **Deterministic variance comments** based on underlying synthetic line items rather than an opaque model response.
- **Reviewer workflow:** `Not Started / In Progress / Reviewed` dropdowns in detailed sheets and live completion percentages in summary sheets.
- **Four-sheet Excel output:** PNL Summary, PNL Quarterly Analysis, BS Summary, and BS Quarterly Analysis.
- **Automated tests + GitHub Actions CI** across Python 3.10–3.12.

## Why this design is faithful to the original problem

The original workflow treated P&L and balance-sheet analysis differently. P&L is period activity, while balance-sheet analysis is about closing balances. The public version preserves that distinction rather than forcing both through one generic variance formula.

It also preserves the original control mindset: normalize inconsistent exports, detect unmapped accounts, retain line-item context for review, flag material movements, and make reviewer progress visible. Employer-specific account logic has been replaced with fictional YAML configuration.

## Architecture

```text
ERP-style synthetic extracts
        |
        v
normalize headers / remove subtotal rows / exact dedup
        |
        v
account mapping + unmapped-account detection
        |
        +---------------------------+
        |                           |
        v                           v
P&L quarter activity           BS quarter-end balance
(GL line items)                (TB preferred / GL fallback)
        |                           |
        +-------------+-------------+
                      v
        QoQ delta / % / YTD / trend / materiality
                      |
                      v
       deterministic variance comments + insights
                      |
                      v
 PNL Summary / PNL Quarterly / BS Summary / BS Quarterly
                      |
                      v
       review-status dropdown + completion tracking
```

See [`docs/architecture.md`](docs/architecture.md) for the same flow in a compact technical view.

## Repository structure

```text
finance-tax-variance-automation/
├── .github/workflows/ci.yml
├── config/
│   └── portfolio_config.yaml
├── data/
│   └── README.md
├── docs/
│   └── architecture.md
├── scripts/
│   └── generate_synthetic_data.py
├── src/
│   ├── analysis.py
│   ├── commentary.py
│   ├── config_loader.py
│   ├── ingestion.py
│   ├── mapping.py
│   ├── pipeline.py
│   └── report_writer.py
├── tests/
├── run_pipeline.py
├── requirements.txt
└── README.md
```

## Run locally

```bash
pip install -r requirements.txt
python scripts/generate_synthetic_data.py
python run_pipeline.py
```

The generator creates fictional P&L GL, balance-sheet GL, and Trial Balance files under `data/raw/`. The pipeline writes a timestamped Excel workbook under `data/output/`.

Run tests with:

```bash
python -m pytest tests/ -v
```

## Public-data design

The demo intentionally includes several conditions a finance automation should handle:

- different column-header variants across quarterly exports;
- subtotal/spacer rows that should not enter calculations;
- an exact duplicate row to prove duplicate handling;
- both P&L and BS accounts;
- a missing BS Trial Balance row to demonstrate conservative zero handling when a zero-suppressed record is absent.

All amounts and identifiers are fictional.

## Accounting logic represented

### P&L

The pipeline aggregates activity by entity, account, and quarter. Account-specific display/sign conventions are configured in `portfolio_config.yaml`. YTD equals the sum of current-year quarter activity through the latest available quarter.

### Balance sheet

The pipeline prefers Trial Balance closing balances for each entity/account/quarter. If Trial Balance data is entirely unavailable, it can fall back to cumulative GL activity. When TB exists but a specific row is absent, the public implementation treats the missing record as zero rather than silently reconstructing a closing balance from unrelated assumptions.

### Materiality and review

A row is flagged when a quarterly balance/activity or its latest QoQ movement exceeds the configured absolute materiality threshold. The detailed sheets retain transaction context and include a reviewer-status dropdown. The summary sheets calculate review completion directly from those detailed statuses.

## What was intentionally *not* copied from the original system

- employer name or identifiers;
- real company codes or account numbers;
- internal SAP report names;
- real tax-account mappings or thresholds;
- original file/folder names;
- production source code;
- company-specific dashboard categories.

The public summary is deliberately generalized to entity-level totals and review metrics.

## AI-assisted development

AI tools were used as a development and learning aid during portfolio construction. Financial logic, expected behavior, synthetic test cases, and controls were reviewed and validated explicitly rather than accepting generated output blindly.

## License

MIT. Synthetic data and fictional business rules only.
