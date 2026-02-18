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

In `config/settings.yaml`, set `enabled: true` under `dashboard:`, then run the experiment. Open `http://127.0.0.1:8765` to see the force-directed swarm graph.

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

## Roadmap

- [x] Core engine (agent, pool, router, db, pairing, emergence)
- [x] 10 starter traditions
- [x] Live dashboard (D3.js force graph + WebSocket feed)
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
