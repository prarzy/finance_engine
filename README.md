<div align="center">

# Finova

### Multi-hop payment routing engine — compare every path, find the cheapest route, send with confidence.

<br/>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-121212?style=flat-square&logo=fastapi" />
  <img src="https://img.shields.io/badge/React-121212?style=flat-square&logo=react" />
  <img src="https://img.shields.io/badge/PostgreSQL-121212?style=flat-square&logo=postgresql" />
  <img src="https://img.shields.io/badge/NetworkX-121212?style=flat-square" />
  <img src="https://img.shields.io/badge/Vite-121212?style=flat-square&logo=vite" />
  <img src="https://img.shields.io/badge/JWT-121212?style=flat-square&logo=jsonwebtokens" />
</p>

<br/>

> Most payment systems optimize for convenience.  
> Finova optimizes for cost — across every route, every hop.

</div>

---

## What it does

Every international transfer hides small losses — FX spreads, fixed fees, percentage markups. Finova doesn't just compare methods: it models the entire payment network as a **directed weighted graph** and uses **Dijkstra's algorithm** to find the cheapest path, including multi-hop routes that route money through intermediate currencies.

Instead of asking *"which method is cheapest?"*, Finova asks *"what is the cheapest sequence of rails?"*

**Single-hop** (before):
```
USD → Wise → EUR
```

**Multi-hop** (now):
```
INR → Bank Transfer → USD → Revolut → EUR   ($4.00 vs $30.00 direct)
```

---

## New in this version

| Feature | Description |
|---|---|
| **Multi-hop routing** | Chains payment rails through intermediate currencies (max 3 hops) |
| **Route path visualization** | `[INR] → [Bank Transfer] → [USD] → [Revolut] → [EUR]` displayed inline |
| **Step-by-step breakdown** | Per-hop FX cost, fees, and settlement time — collapsible |
| **Dynamic currency selection** | Dropdown selectors with live symbol update (₹, $, €, £, د.إ) |
| **Savings comparison** | Best vs. worst ranked, savings ribbon on results screen |
| **PostgreSQL** | Production-grade database with JSONB route storage and indexes |
| **Route explainability** | Priority-ranked natural language explanations for route selection and exclusions |
| **User Dashboard** | Premium dashboard displaying statistics, top corridors chart, and recent transaction history |

---

## Routing algorithm

```
Graph nodes:
  Currencies : "USD", "EUR", "INR", "GBP", "AED"
  Methods    : "wise__USD__EUR", "revolut__USD__EUR", ...

Graph edges:
  currency → method_instance   weight = 0        (enter the rail)
  method_instance → currency   weight = total_cost (fx + fixed + variable fees)

Solver:
  nx.dijkstra_path(G, source_currency, target_currency)       → optimal route
  nx.all_simple_paths(G, source, target, cutoff=7)            → all routes (max 3 hops)
```

### Cost formula per rail step
```
amount_usd    = amount × live_mid_market_rate
fx_cost       = amount_usd × (spread% / 100)
variable_fee  = amount_usd × (variable% / 100)
step_cost     = fx_cost + fixed_fee + variable_fee
```

---

## Payment rails

| Method | FX Spread | Fixed Fee | Variable Fee | Settlement |
|---|---|---|---|---|
| Revolut | 0.20% | $0.00 | 0.00% | Instant |
| Wise | 0.45% | $0.60 | 0.45% | 1 day |
| Crypto | 0.50% | $1.00 | 0.50% | Instant |
| Bank Transfer | 1.50% | $5.00 | 0.00% | 2 days |
| Debit Card | 1.80% | $0.30 | 1.50% | Instant |
| Credit Card | 2.50% | $0.30 | 2.90% | Instant |
| PayPal | 3.00% | $0.30 | 3.49% | Instant |

---

## System flow

```text
User Input (amount · source currency · target currency · methods)
    ↓
Live mid-market rate fetch (ExchangeRate-API → Frankfurter fallback → 5-min cache)
    ↓
PaymentGraph.build()
  └─ For each method × supported currency pair:
       Add edges: currency → method_node (cost=0)
                  method_node → currency (cost=fx+fees)
    ↓
nx.all_simple_paths(G, source, target, cutoff=7)
  └─ Enumerate all valid paths up to 3 rail hops
  └─ Score each path by total edge weight
  └─ Sort → return top 10
    ↓
nx.dijkstra_path(G, source, target)
  └─ Optimal single path (recommended route)
    ↓
AnalyzeResponse
  └─ recommended : { path, steps[], total_cost_usd, hop_count, ... }
  └─ all_routes  : [ ...10 routes ranked by cost... ]
  └─ savings_vs_worst_usd
    ↓
PostgreSQL: INSERT transaction + N route rows (with JSONB path and breakdown)
    ↓
React frontend renders:
  QueryRecap bar · Savings ribbon · SummaryCard hero · RouteCardList (collapsible steps)
```

---

## Stack

### Backend
```yaml
Language:      Python 3.11+
Framework:     FastAPI (async)
Graph Engine:  NetworkX 3.x (Dijkstra + all_simple_paths)
Database:      PostgreSQL 16 + asyncpg (async) + psycopg2 (Alembic)
ORM:           SQLAlchemy 2.0 (async sessions)
Migrations:    Alembic (3 revisions)
Auth:          JWT HS256 (python-jose) + bcrypt 4.0.1 (passlib)
FX APIs:       ExchangeRate-API (primary) · Frankfurter (fallback)
Cache:         In-memory TTL (5 min) per currency pair
Explainability:ExplanationService (priority-ranked deterministic rule engine)
```

### Frontend
```yaml
Framework:     React 19 + Vite
Styling:       Tailwind CSS + custom design tokens
Fonts:         Cormorant Garamond (headings) · DM Mono (numbers)
State:         useAnalyze custom hook
API client:    services/api.js (fetch + OAuth2 form-encoded login)
Route UI:      RoutePathFlow · StepBreakdown · SummaryCard · RouteCard · DashboardPage · SupportedRoutesPage
```

---

## Repository structure

```
finance_engine/
│
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── auth.py              # /register  /login  /me
│   │   │   ├── analyze.py           # /analyze  /recommend  /history
│   │   │   ├── corridors.py         # /check-limits  /corridors
│   │   │   ├── dashboard.py         # /dashboard/summary
│   │   │   └── schemas.py           # Pydantic models (RouteStepOut, RouteOut, ...)
│   │   ├── core/
│   │   │   ├── graph.py             # PaymentGraph — multi-hop Dijkstra engine
│   │   │   ├── security.py          # JWT + bcrypt
│   │   │   ├── config.py            # pydantic-settings
│   │   │   └── cache.py             # In-memory FX rate TTL cache
│   │   ├── services/
│   │   │   ├── fx_service.py        # ExchangeRate-API + Frankfurter fallback
│   │   │   ├── explanation_service.py # Route explainability (Dijkstra decision reasons)
│   │   │   └── route_analyzer.py    # Orchestrates graph build + route ranking
│   │   ├── models/
│   │   │   ├── user.py              # UUID PK, bcrypt password
│   │   │   ├── transaction.py       # + hop_count, route_path JSONB
│   │   │   ├── route.py             # + hop_count, path JSONB, breakdown JSONB
│   │   │   ├── currency.py          # Currencies table
│   │   │   ├── provider.py          # Providers table
│   │   │   ├── provider_corridor.py # Provider corridor constraints
│   │   │   └── compliance_rule.py   # Compliance rules
│   │   └── db/database.py           # asyncpg engine, pool_size=10
│   ├── alembic/versions/
│   │   ├── 5a9165c30fb6_create_initial_tables.py
│   │   ├── a1b2c3d4e5f6_multihop_postgresql.py   # JSONB cols + indexes
│   │   └── b1c2d3e4f5a6_add_constraint_tables.py  # Corridor + Compliance tables
│   ├── seed_constraints.py          # Seeds 9 currencies, 4 providers, ~280 corridors
│   └── seed_user.py                 # Add users to PostgreSQL via psycopg2
│
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── AuthPanel.jsx         # Login / Register
│       │   ├── PaymentForm.jsx       # Amount + currency dropdowns + method chips
│       │   ├── QueryRecap.jsx        # Summary bar above results
│       │   ├── ResultsPanel.jsx      # Savings ribbon + cards
│       │   ├── SummaryCard.jsx       # Recommended route hero card
│       │   ├── RouteCard.jsx         # Route row with mini bars + StepBreakdown
│       │   ├── RouteCardList.jsx     # Ranked list of routes
│       │   ├── RoutePathFlow.jsx     # [INR] → [Wise] → [USD] horizontal display
│       │   └── StepBreakdown.jsx     # Collapsible per-hop cost detail
│       ├── pages/
│       │   ├── Auth.jsx              # Modal-based authentication
│       │   ├── Analyze.jsx           # Payment routing form
│       │   ├── Dashboard.jsx         # Static dashboard landing
│       │   ├── DashboardPage.jsx     # Premium statistics & activity dashboard
│       │   ├── History.jsx           # Transaction history list
│       │   ├── SupportedRoutes.jsx   # Older corridors browser
│       │   └── SupportedRoutesPage.jsx # Premium corridors browser with info banners
│       ├── hooks/
│       │   ├── useAuth.js            # Authentication state hook
│       │   └── useAnalyze.js         # Form state + API call + limit check debounce
│       ├── services/api.js           # Fetch API wrappers
│       └── utils/routeUtils.js       # parsePath, formatMethodName, symbolFor
```

---

## Local setup

### 1. Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 16

### 2. Clone
```bash
git clone https://github.com/prarzy/finance_engine.git
cd finance_engine
```

### 3. Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Create `.env`

```env
APP_ENV=development

SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/finova
DATABASE_URL_SYNC=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/finova

EXCHANGERATE_API_KEY=<your key from exchangerate-api.com>
FX_CACHE_TTL_SECONDS=300

ALLOWED_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

### 5. Create database and run migrations

```bash
# Create the database (run in psql or pgAdmin)
createdb finova

# Run Alembic migrations
alembic upgrade head

# Seed constraints (currencies, providers, corridors)
python seed_constraints.py

# Seed a user
python seed_user.py your@email.com yourpassword

# Start the backend
uvicorn app.main:app --reload --port 8000
```

API docs: **http://localhost:8000/docs**

### 8. Start the frontend

```bash
cd ../frontend
npm install
npm run dev
```

App: **http://localhost:5173**

---

## API endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | — | Create account |
| `POST` | `/api/v1/auth/login` | — | OAuth2 login → JWT |
| `GET`  | `/api/v1/auth/me` | ✓ | Current user profile |
| `POST` | `/api/v1/analyze` | optional | Multi-hop route analysis |
| `GET`  | `/api/v1/recommend` | — | Quick recommendation |
| `GET`  | `/api/v1/history` | ✓ | Past transactions |
| `POST` | `/api/v1/check-limits` | — | Pre-validate transfer limits |
| `GET`  | `/api/v1/corridors` | — | Supported corridors grouped by provider |
| `GET`  | `/api/v1/dashboard/summary` | ✓ | User dashboard summary statistics |
| `GET`  | `/health` | — | Health check |

### Example response (`/analyze`)

```json
{
  "amount": 1000.0,
  "source_currency": "INR",
  "target_currency": "EUR",
  "mid_market_rate": 0.0112,
  "amount_usd": 11.2,
  "recommended": {
    "method_name": "multi_hop",
    "total_cost_usd": 4.25,
    "fx_spread_pct": 0.0,
    "fx_cost_usd": 0.0,
    "fixed_fee_usd": 0.0,
    "variable_fee_pct": 0.0,
    "variable_fee_usd": 0.0,
    "processing_days": 1,
    "settlement_hours": 24,
    "rank": 1,
    "is_recommended": true,
    "hop_count": 2,
    "path": ["INR", "wise__INR__USD", "USD", "revolut__USD__EUR", "EUR"],
    "currency_path": ["INR", "USD", "EUR"],
    "steps": [
      {
        "from_currency": "INR",
        "method": "wise",
        "to_currency": "USD",
        "fx_spread_pct": 0.45,
        "fx_cost_usd": 0.08,
        "fixed_fee_usd": 0.60,
        "variable_fee_pct": 0.45,
        "variable_fee_usd": 0.34,
        "step_cost_usd": 1.02,
        "processing_days": 1
      }
    ],
    "explanations": [
      "Lowest total cost among all valid routes.",
      "$12.50 cheaper than the next best alternative."
    ]
  },
  "all_routes": [
    {
      "method_name": "multi_hop",
      "total_cost_usd": 4.25,
      "fx_spread_pct": 0.0,
      "fx_cost_usd": 0.0,
      "fixed_fee_usd": 0.0,
      "variable_fee_pct": 0.0,
      "variable_fee_usd": 0.0,
      "processing_days": 1,
      "settlement_hours": 24,
      "rank": 1,
      "is_recommended": true,
      "hop_count": 2,
      "path": ["INR", "wise__INR__USD", "USD", "revolut__USD__EUR", "EUR"],
      "currency_path": ["INR", "USD", "EUR"],
      "steps": [],
      "explanations": []
    }
  ],
  "savings_vs_worst_usd": 53.28,
  "savings_vs_worst_pct": 475.71,
  "timestamp": "2026-06-04T14:48:00.000000Z"
}
```

---

## Security

| Layer | Implementation |
|---|---|
| Authentication | JWT HS256, 24h expiry |
| Passwords | bcrypt hashing (passlib + bcrypt 4.0.1) |
| CORS | Configured via `ALLOWED_ORIGINS` |
| DB | No PII beyond email stored |

---

## Roadmap

| Feature | Status | Description |
|---|---|---|
| **History & Dashboard** | Completed | Transaction history with savings tracking and charts |
| **Explainability Engine** | Completed | Deterministic prioritised natural language explanations |
| **More currencies** | Partially Done | JPY, SGD, CAD, AUD completed. CHF upcoming |
| **More rails** | Upcoming | SEPA, SWIFT, UPI, Stripe |
| **Best time to pay** | Upcoming | ML-based FX timing |
| **Browser extension** | Upcoming | Checkout overlay with optimal route |

---

<div align="center">

Built to make digital payments transparent, measurable, and optimizable.

**Fin·o·va**

</div>
