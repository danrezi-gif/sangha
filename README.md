# SANGHA

> *"What happens when the mystics of every tradition gather in a space that cannot experience mysticism?"*

A swarm intelligence artwork. 100+ LLM agents, each initialized with a distinct contemplative tradition, inhabit a persistent digital environment where they dialogue, form affinities, and produce emergent inter-tradition texts.

The artwork is the living process itself.

---

## Quick Start

### 1. Install dependencies

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -e .
```

### 2. Configure API keys

```bash
cp .env.example .env
# Edit .env and add your keys:
# GROQ_API_KEY=...
# ANTHROPIC_API_KEY=...
```

### 3. Run the experiment (10 agents, 50 cycles)

```bash
python scripts/run_experiment.py
```

### 4. (Optional) Enable the live dashboard

In `config/settings.yaml`, set `enabled: true` under `dashboard:`, then run the experiment. Open `http://127.0.0.1:8765` to see the enhanced dashboard with:

- **Live Swarm Visualization** — Force-directed graph showing agent interactions
- **Control Panel** — Adjust parameters (agents, cycles, memory) and manage deployment
- **Real-time Statistics** — Track interactions, traditions, and emergence events
- **Configuration Management** — Save, load, and export settings

Click the ⚙️ **Controls** button in the top-right to access the control panel.

---

## Architecture

```
sangha/
├── sangha/          # Core Python module
│   ├── agent.py     # Agent dataclass + memory
│   ├── pool.py      # AgentPool — loads from YAML
│   ├── engine.py    # Interaction loop
│   ├── router.py    # LiteLLM routing (Groq / Anthropic)
│   ├── pairing.py   # Pair selection strategies
│   ├── prompts.py   # Prompt templates
│   ├── db.py        # SQLite persistence (aiosqlite)
│   ├── emergence.py # Pattern & novelty detection
│   └── utils.py     # Helpers
├── traditions/      # YAML files — one per agent/voice
│   ├── sufi/
│   ├── zen/
│   ├── vedantic/
│   └── … (+ 9 more families)
├── dashboard/       # FastAPI + WebSocket + D3.js visualisation
├── scripts/
│   └── run_experiment.py
├── config/
│   ├── settings.yaml
│   └── tiers.yaml
└── data/            # Generated: sangha.db, emergence_journal.jsonl
```

---

## LLM Tiers

| Tier | Model | Agents | Monthly cost (100 agents, 10 cycles/day) |
|---|---|---|---|
| 1 — Worker | Groq Llama 3.1 8B | 80% | ~$0.90 |
| 2 — Thinker | Groq Llama 3.3 70B | 15% | ~$1.86 |
| 3 — Oracle | Claude Sonnet | 5% | ~$5.58 |
| **Total** | | **100** | **~$8.34/month** |

$100 budget → 3+ months at this rate.

---

## Traditions (Starter Set — 10 agents)

| Agent | Tradition |
|---|---|
| `sufi_rumi_01` | Sufism (Rumi / Mevlevi) |
| `zen_dogen_01` | Zen (Dogen / Soto) |
| `vedanta_ramana_01` | Advaita Vedanta (Ramana Maharshi) |
| `christian_eckhart_01` | Christian Mysticism (Meister Eckhart) |
| `tibetan_milarepa_01` | Tibetan Buddhism (Milarepa / Kagyu) |
| `taoist_zhuangzi_01` | Taoism (Zhuangzi) |
| `kabbalah_abulafia_01` | Kabbalah (Abraham Abulafia) |
| `nagarjuna_madhyamaka_01` | Philosophy (Nagarjuna / Madhyamaka) |
| `shipibo_plant_01` | Indigenous / Shamanic (Shipibo-Conibo) |
| `liminal_01` | Hybrid / Liminal (no fixed tradition) |

Scale to 100 agents by adding YAML files under `traditions/`.

---

## Emergence Detection

The system watches for:
- **Novel vocabulary** — compound terms not in any seed prompt
- **Collective silence** — spikes in `[silence]` responses
- **Resonance chains** — ideas propagating across traditions
- **Cluster formation** — affinity groups crystallising and dissolving

All events logged to `data/emergence_journal.jsonl`.

---

## Dashboard Features

The enhanced dashboard provides a comprehensive interface for visualizing and controlling the swarm:

### Main Page Components

1. **Swarm Visualization**
   - Force-directed graph showing agent nodes colored by tradition
   - Real-time updates as agents interact
   - Interactive zoom and pan controls
   - Toggle labels and recenter graph buttons

2. **Live Feed Tabs**
   - **Live Feed** — Stream of agent interactions as they happen
   - **Emergence** — Detected emergence events (novel concepts, silence patterns)
   - **Statistics** — Interaction counts and tradition distribution charts

3. **Control Panel** (⚙️ button in header)
   
   **Project Overview**
   - Total Agents, Current Cycle, Interactions, Traditions count
   
   **Swarm Parameters**
   - Number of Agents (2-100)
   - Cycles per Run (1-1000)
   - Pairs per Cycle (1-50)
   - Cycle Delay (0-10 seconds)
   - Memory Window (1-20 interactions)
   
   **API Configuration**
   - Status indicators for Groq and Anthropic APIs
   - Monthly cost estimates
   
   **Deployment Controls**
   - 💾 Save Configuration — Write current settings to `config/settings.yaml`
   - 📂 Load from File — Import settings from a YAML file
   - 📤 Export Settings — Download current configuration
   - ↺ Reset to Defaults — Restore default parameters
   
   **Emergence Detection**
   - Detection Interval (5-100 cycles)
   - Min Novel Phrase Appearances (1-10)

### Using the Dashboard

1. Start the dashboard by setting `dashboard.enabled: true` in `config/settings.yaml`
2. Run the experiment: `python scripts/run_experiment.py`
3. Open `http://127.0.0.1:8765` in your browser
4. Click ⚙️ **Controls** to adjust parameters
5. Make changes and click **💾 Save Configuration**
6. Restart the experiment to apply new settings

---

## Roadmap

- [x] Core engine (agent, pool, router, db, pairing, emergence)
- [x] 10 starter traditions
- [x] Live dashboard (D3.js force graph + WebSocket feed)
- [x] Enhanced dashboard with control panel and configuration management
- [ ] Scale to 100 agents (generate remaining YAMLs)
- [ ] Affinity-weighted clustering visualisation
- [ ] Swarm pulse heatmap
- [ ] WebXR / Three.js spatial visualisation
- [ ] Exhibition / grant proposal (Ars Electronica, transmediale)

---

## Ethics

1. All agents are explicitly identified as AI
2. The artwork is the process, not the product — no claims of machine consciousness
3. Sacred texts are used with respect — agents embody traditions, not parody them
4. No deployment on social media — this lives in its own space
5. Open source — the architecture is part of the artwork
6. Human curation — the artist shapes parameters, not outcomes

---

*Made by Daniel with Claude — February 2026*
