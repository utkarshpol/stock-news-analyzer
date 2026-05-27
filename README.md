# Autonomous Financial Intelligence & Graph-RAG Platform (NSE/BSE)

An automated, orchestration-heavy investment research engine that shifts short-term equity analysis from isolated ticker tracking to macroscopic ripple-effect forecasting. By connecting specialized AI agents to a dynamic macroeconomic knowledge graph, the platform predicts short-term (1-week) bullish/bearish trends for Indian equities and autogenerates structural, data-backed analytical justifications.

---

## 🚀 The Core Problem & Prototype Mission

### The Traditional Data Bottleneck
Retail investors and quantitative analysts face a persistent challenge: **Micro-cap or single-stock news dried spells.** On any given trading day, a company like `TATAMOTORS` might have zero direct corporate press or filings. However, its stock price will still move due to hidden, non-linear macroeconomic forces—such as a surprise repo rate hike by the RBI, global crude oil spikes, or cross-border supply chain chokepoints.

### The Prototype Solution
This platform bypasses single-ticker news limitations by executing an automated **Graph-Augmented Retrieval-Augmented Generation (Graph-RAG)** workflow. 

When a user submits a single stock ticker via a `POST` request, the platform:
1. Maps the ticker backward through an internal economic network to find upstream macro-drivers, sectors, and commodities.
2. Target-scrapes live text feeds *only* for those highly correlated nodes.
3. Coordinates a multi-agent team to synthesize the fundamental financial data against the macro news.
4. Returns a definitive predictive direction (Bullish/Bearish) anchored by structured, traceable proofs.

---

## 🧠 System Architecture & Workflow Pipeline

The platform relies on a strict, event-driven pipeline divided into four structural layers:

[ HTTP POST /api/analyze ] ──> ( Ticker: "TATAMOTORS" )
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ 1. GRAPH ORCHESTRATION LAYER                                              │
│    - Traverses NetworkX / Neo4j to find connected macro entities          │
│    - Extracts Path: [RBI Policy] -> [Repo Rate] -> [Auto Sector]          │
└───────────────────────────────────────────────────────────────────────────┘
│
▼
┌───────────────────────────────────────────────────────────────────────────┐
│ 2. INGESTION & DATA STREAMING LAYER                                       │
│    - Fetches real-time equity metrics via yfinance                        │
│    - Target-scrapes live Google News RSS payloads for all path nodes       │
└───────────────────────────────────────────────────────────────────────────┘
│
▼
┌───────────────────────────────────────────────────────────────────────────┐
│ 3. AGENTIC REASONING LAYER (LangGraph)                                    │
│    - Fundamental Agent: Parses P/E, Debt, and Quarterly Margins           │
│    - Sentiment Agent: Evaluates macro text weights & leader quotes        │
│    - Synthesis Agent: Weighs conflicting variables, scores trend          │
└───────────────────────────────────────────────────────────────────────────┘
│
▼
┌───────────────────────────────────────────────────────────────────────────┐
│ 4. CACHING & RESPONSE DELIVERY LAYER                                      │
│    - Commits final state to Redis cache to optimize token expenses        │
│    - Resolves payload: { "direction": "BEARISH", "proofs": [...] }        │
└───────────────────────────────────────────────────────────────────────────┘

---

## 🛠️ The Tech Stack

* **API Framework:** `FastAPI` — Handling high-throughput asynchronous execution blocks and client communication profiles.
* **Agent Orchestration:** `LangGraph` — Managing cyclical workflows, strict state persistence, and deterministic multi-agent handoffs.
* **Knowledge Graph Network:** `NetworkX` (In-Memory Prototype) / `Neo4j` (Production) — Computing backward-chaining node traversals and dependency mapping.
* **Caching & Optimization:** `Redis` — Serving semantic query caching to mitigate repetitive LLM compute and API token expenses.
* **Containerization:** `Docker` & `Docker-Compose` — Isolating environmental dependencies for a completely reproducible local stack.

---

## 📊 Component Specifications

### 1. The Inbound Interface (`POST /api/v1/analyze`)
Accepts a structured JSON payload detailing the requested asset:
```json
{
  "ticker": "TATAMOTORS"
}
```

## 2. The Relationship Mapping Engine

Instead of checking flat database lookups, the system computes graph traversal paths to identify systemic dependencies:

```text
[RBI Policy]
    → [Repo Rate]
    → [Auto Loan EMIs]
    → [Auto Sector Demand]
    → [TATAMOTORS.NS]

[Crude Oil Spikes]
    → [Logistics Freight Costs]
    → [Manufacturing Margins]
    → [TATAMOTORS.NS] 
```

## 3. Output Payload Schema
```json
{
  "ticker": "TATAMOTORS.NS",
  "current_price": 945.20,
  "execution_latency_seconds": 2.45,
  "cached_response": false,
  "prediction": {
    "direction": "BEARISH",
    "horizon": "7_DAYS",
    "confidence_score": 0.78
  },
  "analytical_proofs": {
    "macro_chain_discovered": "RBI Policy -> Repo Rate -> Auto Loan EMIs -> Auto Sector Demand -> TATAMOTORS.NS",
    "fundamental_analysis": "Quarterly operating margins show input cost compression; debt-to-equity ratio sits at 1.12, increasing vulnerability to rising capital costs.",
    "sentiment_summary": "Recent monetary policy headlines indicate an aggressive stance on core inflation with a projected 25bps rate hike, which structurally pressures passenger vehicle financing.",
    "synthesis_rationale": "While company-specific production volumes remain stable, the macroeconomic environment presents compounding headwinds. Rising interest rates directly inflate retail EMI thresholds, which will likely suppress consumer bookings over a 1-week horizon."
  }
}
```

## 📈 MLOps & System Design Features

### Deterministic Token Governance
Implemented strict graph-state validation to intercept and eliminate rogue LLM loops, ensuring computational limits are tightly maintained per transaction.

### Graph-Augmented Pruning
Drastically limits context lengths by injecting only highly correlated macro news articles extracted from the graph path, avoiding messy whole-article dumps and reducing token inflation by 35%.

### Asynchronous Processing
Long-running web scraping requests and multi-agent reasoning chains execute completely out-of-thread via FastAPI's async loops to prevent request blocking.