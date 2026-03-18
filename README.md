# RealVest CRM

A lightweight CRM for real estate companies to track investors and their property portfolios.

## Features

- **Investor Management** — Track individuals, funds, and institutional investors with contact details, status, and notes
- **Property Portfolio** — Attach properties to investors with full financial details (purchase price, current value, equity, rent, cap rate)
- **Dashboard** — Live summary of total portfolio value, monthly rent, equity, and property counts
- **Filtering & Search** — Search investors by name/email/company; filter properties by type and status
- **Investor Drawer** — Click any investor to see their full profile and property portfolio in a side drawer

## Stack

- **Backend:** Python / Flask + SQLAlchemy (SQLite)
- **Frontend:** Vanilla HTML / CSS / JavaScript (no build step)

## Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# (Optional) Seed sample data
python seed.py

# Run the server
python app.py
```

Then open http://localhost:5000

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/investors | List investors (supports `?q=` search, `?status=`) |
| POST | /api/investors | Create investor |
| GET | /api/investors/:id | Get investor + properties |
| PUT | /api/investors/:id | Update investor |
| DELETE | /api/investors/:id | Delete investor |
| GET | /api/properties | List properties (supports `?investor_id=`, `?status=`, `?property_type=`) |
| POST | /api/properties | Create property |
| GET | /api/properties/:id | Get property |
| PUT | /api/properties/:id | Update property |
| DELETE | /api/properties/:id | Delete property |
| GET | /api/stats | Dashboard statistics |

## Data Model

**Investor**
- name, email, phone, company
- investor_type: `individual` | `institutional` | `fund`
- status: `active` | `inactive` | `prospect`

**Property**
- investor (FK), address, city, state, zip
- property_type: `residential` | `commercial` | `industrial` | `land`
- purchase_price, current_value, purchase_date
- square_feet, units, monthly_rent, status
- Computed: equity, annual_rent, cap_rate
