<div align="center">

# Smart Payment Route Optimizer

### Real-time payment path optimization for minimizing FX spreads, fees, and routing inefficiencies.

<br/>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-121212?style=flat-square&logo=fastapi" />
  <img src="https://img.shields.io/badge/React-121212?style=flat-square&logo=react" />
  <img src="https://img.shields.io/badge/PostgreSQL-121212?style=flat-square&logo=postgresql" />
  <img src="https://img.shields.io/badge/NetworkX-121212?style=flat-square" />
  <img src="https://img.shields.io/badge/TailwindCSS-121212?style=flat-square&logo=tailwindcss" />
  <img src="https://img.shields.io/badge/JWT-121212?style=flat-square&logo=jsonwebtokens" />
</p>

<br/>

> Most payment systems optimize for convenience.  
> This one optimizes for cost.

</div>

---

## What it does

Every online payment hides small losses:

- FX spreads
- processor markups
- conversion fees
- inefficient routing
- timing slippage

This project models digital payment systems as weighted graphs and computes the cheapest possible transaction route before payment execution.

Users can compare multiple payment rails in real time and see exactly where money is being lost.

---

## Core Optimization Model

| Graph Component | Representation |
|---|---|
| Nodes | Banks, wallets, cards, currencies |
| Edges | Transaction paths |
| Weights | FX spread + fees + slippage |
| Solver | Shortest-path optimization |

---

## Feature Set

<div align="center">

| Optimization Engine | FX Intelligence | Analytics |
|---|---|---|
| Multi-route comparison | Live exchange-rate integration | Savings visualization |
| Dynamic edge-cost modelling | Spread estimation | Cost breakdowns |
| Smart payment ranking | Real-time conversion logic | Historical tracking |

</div>

<br/>

<div align="center">

| Security | Infrastructure | UX |
|---|---|---|
| JWT Authentication | Neon PostgreSQL | Responsive UI |
| AES-256 Encryption | FastAPI Backend | Interactive dashboards |
| Secure Sessions | Modular APIs | Route comparison cards |

</div>

---

## System Flow

```text
User Input
    ↓
Payment Graph Construction
    ↓
Dynamic Cost Assignment
    ↓
Route Optimization Engine
    ↓
Ranked Recommendations
    ↓
Frontend Visualization
```

---

# Stack

## Backend

```yaml
Framework: FastAPI
Language: Python 3.11+
Graph Engine: NetworkX
Database: PostgreSQL (Neon)
Authentication: JWT
```

---

## Frontend

```yaml
Framework: React 18
Styling: Tailwind CSS
Charts: Recharts
```

---

## APIs

```yaml
Exchange Rates:
  - ExchangeRate API
  - Frankfurter API
```

---

## Example Analysis

### Input

```json
{
  "amount": 1000,
  "source_currency": "INR",
  "target_currency": "USD",
  "methods": [
    "Card",
    "Wallet",
    "Bank Transfer"
  ]
}
```

---

### Output

```text
[1] INR → Credit Card → USD
Estimated Cost: ₹412

[2] INR → Wallet → Bank Transfer → USD
Estimated Cost: ₹287   ← Optimal Route
```

---

## Cost Model

```text
Total Cost =
FX Spread +
Transaction Fees +
Slippage
```

---

## Repository Structure

```bash
smart-payment-route-optimizer/
│
├── backend/
│   ├── app/
│   ├── routes/
│   ├── services/
│   ├── models/
│   └── tests/
│
├── frontend/
│   ├── components/
│   ├── pages/
│   ├── charts/
│   └── utils/
│
├── docs/
└── README.md
```

---

# Local Setup

## Clone Repository

```bash
git clone <repository-url>
cd smart-payment-route-optimizer
```

---

## Backend Setup

```bash
cd backend

python -m venv venv
```

### Activate Virtual Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / macOS

```bash
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file inside `backend/`

```env
DATABASE_URL=your_neon_postgresql_url
JWT_SECRET=your_secret_key
EXCHANGE_RATE_API_KEY=your_api_key
```

---

## Start Backend

```bash
uvicorn app.main:app --reload
```

---

## Frontend Setup

```bash
cd frontend

npm install
npm run dev
```

---

# Testing

```bash
pytest
```

```bash
npm test
```

```bash
npx playwright test
```

---

# Security

| Layer | Implementation |
|---|---|
| Authentication | JWT |
| Encryption | AES-256 |
| Transport | HTTPS/TLS |
| Data Handling | Minimal PII collection |

---

# Future Scope

| Feature | Description |
|---|---|
| Best Time to Pay | ML-based FX timing predictions |
| Browser Extension | Checkout overlays with optimal routes |
| Open Banking | Balance-aware recommendations |
| Personalized Profiles | Adaptive routing logic |
| Merchant SDK | Integration for e-commerce platforms |

---

# Performance Targets

| Metric | Goal |
|---|---|
| API p95 Latency | < 500ms |
| Route Accuracy | > 85% |
| Monthly Active Users | 1000+ |
| Avg Savings/User | $20+ |

---

<div align="center">

Built to make digital payments transparent, measurable, and optimizable.

</div>
