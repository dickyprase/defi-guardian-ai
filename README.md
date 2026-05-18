# DeFi Guardian AI

<p align="center">
  <img src="docs/architecture.png" alt="DeFi Guardian AI Architecture" width="600"/>
</p>

> **Multi-Agent DeFi Portfolio Risk Analysis & Fraud Detection Platform** powered by MiMo V2.5 reasoning models.

[![MiMo API](https://img.shields.io/badge/MiMo-V2.5--Pro-blue)](https://platform.xiaomimimo.com)
[![Hermes Agent](https://img.shields.io/badge/Agent-Hermes-green)](https://hermes-agent.nousresearch.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 🎯 Problem Statement

DeFi users face critical risks daily:
- **Rug pulls** drain $2.8B+ annually from unsuspecting investors
- **Smart contract vulnerabilities** lead to exploits worth millions
- **Token economics manipulation** creates artificial pump-and-dump schemes
- **Cross-chain bridge attacks** exploit complex multi-chain interactions

Traditional security tools are reactive — they detect threats *after* damage is done. **DeFi Guardian AI** uses proactive multi-agent reasoning to identify risks *before* they materialize.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DeFi Guardian AI Platform                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Risk Score  │  │  Alert       │  │  Portfolio            │  │
│  │  Dashboard   │  │  System      │  │  Recommendations      │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                  │                      │              │
│  ┌──────┴──────────────────┴──────────────────────┴───────────┐ │
│  │              Agent Orchestrator (Hermes Agent)               │ │
│  │         Long-chain reasoning via MiMo-V2.5-Pro              │ │
│  └──────┬──────────┬──────────┬──────────┬──────────┬─────────┘ │
│         │          │          │          │          │            │
│  ┌──────┴───┐ ┌────┴────┐ ┌──┴───┐ ┌────┴────┐ ┌──┴────────┐  │
│  │Contract  │ │Liquidity│ │Token │ │Whale    │ │Risk       │  │
│  │Auditor   │ │Monitor  │ │Econ  │ │Tracker  │ │Reporter   │  │
│  │Agent     │ │Agent    │ │Agent │ │Agent    │ │Agent      │  │
│  └──────────┘ └─────────┘ └──────┘ └─────────┘ └───────────┘  │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│  Data Layer: Ethereum RPC | BSC | Polygon | Arbitrum | DeFiLlama │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🤖 Agent System

### 1. Contract Auditor Agent
- Decompiles and analyzes smart contract bytecode
- Detects common vulnerability patterns (reentrancy, overflow, access control)
- Uses MiMo-V2.5-Pro for deep reasoning about complex contract logic
- Generates severity-scored audit reports

### 2. Liquidity Monitor Agent
- Real-time monitoring of liquidity pool changes
- Detects sudden liquidity removal (rug pull indicator)
- Tracks LP token holder concentration
- Alerts on abnormal TVL fluctuations

### 3. Token Economics Agent
- Analyzes tokenomics: supply distribution, vesting schedules, unlock events
- Detects inflationary/deflationary manipulation
- Models price impact of large holder movements
- Identifies honeypot token patterns

### 4. Whale Tracker Agent
- Monitors large wallet movements across chains
- Correlates whale activity with price movements
- Identifies coordinated wallet clusters (sybil detection)
- Tracks smart money flow patterns

### 5. Risk Reporter Agent
- Aggregates findings from all agents
- Generates comprehensive risk scores (0-100)
- Produces human-readable reports with actionable recommendations
- Maintains historical risk trend data

---

## 🔧 Tech Stack

| Component | Technology |
|-----------|-----------|
| AI Model | MiMo-V2.5-Pro (reasoning), MiMo-V2.5-Lite (fast analysis) |
| Agent Framework | Hermes Agent (orchestration) |
| Development | Cursor + Claude Code (AI-assisted development) |
| Language | Python 3.11+ |
| Blockchain | Web3.py, ethers.js adapters |
| Database | PostgreSQL (structured), Redis (cache/queue) |
| APIs | DeFiLlama, Etherscan, CoinGecko, GoPlus Security |
| Deployment | Docker + Docker Compose |

---

## 📊 Token Consumption Model

| Agent | Tokens/Request | Requests/Day | Daily Total |
|-------|---------------|-------------|-------------|
| Contract Auditor | ~45,000 | 200 | 9.0M |
| Liquidity Monitor | ~12,000 | 500 | 6.0M |
| Token Economics | ~28,000 | 300 | 8.4M |
| Whale Tracker | ~8,000 | 800 | 6.4M |
| Risk Reporter | ~35,000 | 150 | 5.25M |
| **Total per user** | | | **~35.1M** |
| **100 users (target)** | | | **~3.5B/day** |
| **Monthly projection** | | | **~105B tokens** |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- MiMo API Key ([Get from platform.xiaomimimo.com](https://platform.xiaomimimo.com))
- Ethereum RPC endpoint (Alchemy/Infura)

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/defi-guardian-ai.git
cd defi-guardian-ai
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

```bash
# .env
MIMO_API_KEY=your_mimo_api_key
MIMO_MODEL=mimo-v2.5-pro
MIMO_BASE_URL=https://api.xiaomimimo.com/v1
ETH_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://user:pass@localhost:5432/defi_guardian
```

### Run

```bash
# Start all agents
python -m core.orchestrator

# Run specific agent
python -m agents.contract_auditor --address 0x...

# Start monitoring dashboard
python -m core.dashboard
```

---

## 📁 Project Structure

```
defi-guardian-ai/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py          # Base agent class with MiMo integration
│   ├── contract_auditor.py    # Smart contract security analysis
│   ├── liquidity_monitor.py   # Liquidity pool monitoring
│   ├── token_economics.py     # Tokenomics analysis
│   ├── whale_tracker.py       # Large wallet movement tracking
│   └── risk_reporter.py       # Risk aggregation & reporting
├── core/
│   ├── __init__.py
│   ├── orchestrator.py        # Multi-agent orchestration
│   ├── mimo_client.py         # MiMo API client wrapper
│   ├── blockchain.py          # Multi-chain data fetcher
│   └── dashboard.py           # Risk score dashboard
├── config/
│   ├── agents.yaml            # Agent configuration
│   └── chains.yaml            # Supported chain configs
├── docs/
│   ├── architecture.png
│   └── API.md
├── scripts/
│   ├── setup.sh
│   └── deploy.sh
├── tests/
│   ├── test_agents.py
│   └── test_orchestrator.py
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 🔬 How It Works

### Analysis Pipeline

```
User Request (address/token/protocol)
        │
        ▼
┌─────────────────────┐
│  Agent Orchestrator  │ ← Determines which agents to activate
└─────────┬───────────┘
          │
          ├──→ Contract Auditor (if smart contract)
          ├──→ Liquidity Monitor (if DEX/pool)
          ├──→ Token Economics (if token analysis)
          ├──→ Whale Tracker (if wallet/flow analysis)
          │
          ▼
┌─────────────────────┐
│   Risk Reporter     │ ← Aggregates all agent findings
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Risk Score (0-100) │
│  + Detailed Report  │
│  + Recommendations  │
└─────────────────────┘
```

### MiMo Integration

The platform leverages MiMo-V2.5-Pro's **long-chain reasoning** capabilities for:

1. **Multi-step contract analysis** — Following execution paths through complex proxy patterns
2. **Cross-reference reasoning** — Correlating on-chain data with off-chain signals
3. **Temporal pattern detection** — Identifying time-based manipulation strategies
4. **Risk score calibration** — Weighing multiple risk factors with contextual understanding

---

## 🛡️ Security Features

- **Proactive Detection**: Identifies risks before exploits occur
- **Multi-Chain Coverage**: Ethereum, BSC, Polygon, Arbitrum, Base
- **Real-time Alerts**: Webhook/Telegram notifications for critical risks
- **Historical Analysis**: Track risk evolution over time
- **Zero False Positive Target**: MiMo reasoning reduces noise

---

## 📈 Development Status

- [x] Core architecture design
- [x] MiMo API integration
- [x] Base agent framework
- [x] Contract Auditor Agent (v1)
- [x] Liquidity Monitor Agent (v1)
- [x] Token Economics Agent (v1)
- [ ] Whale Tracker Agent (in progress)
- [ ] Risk Reporter Agent (in progress)
- [ ] Dashboard UI
- [ ] Multi-chain expansion
- [ ] Production deployment

**Current Phase**: Active development — seeking MiMo API credits for testing and production scale.

---

## 🤝 Built With

- **[MiMo V2.5](https://platform.xiaomimimo.com)** — Core reasoning engine
- **[Hermes Agent](https://hermes-agent.nousresearch.com)** — Agent orchestration
- **[Cursor](https://cursor.sh)** + **Claude Code** — AI-assisted development

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- Xiaomi MiMo team for the powerful reasoning models
- Hermes Agent community for the orchestration framework
- DeFi security researchers for vulnerability databases
