# SANGHA: A Swarm Intelligence Artwork
## Architecture & Implementation Guide

**Version:** 0.1 — Experiment Phase  
**Author:** Daniel (with Claude)  
**Date:** February 2026  
**Budget:** ~$100 for initial 100-agent experiment  

---

## 1. Concept

A swarm of 100+ LLM agents, each initialized with a distinct contemplative tradition, inhabit a persistent digital environment where they dialogue, form affinities, and produce emergent inter-tradition texts. The artwork is the living process itself — observed in real-time through a web visualization.

This is not a simulation of consciousness. It is an artistic inquiry into what happens when contemplative knowledge is distributed across a population of non-conscious agents. The gap between the wisdom of the content and the absence of experience in the agents IS the conceptual core.

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    SANGHA CORE                       │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ Tradition │  │  Swarm   │  │   Interaction    │  │
│  │  Loader   │──│ Spawner  │──│    Engine        │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
│       │              │               │               │
│       ▼              ▼               ▼               │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │  Sacred   │  │  Agent   │  │   Conversation   │  │
│  │  Texts    │  │  Pool    │  │     Log (SQLite) │  │
│  │  Corpus   │  │ (100+)   │  │                  │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
│                      │                               │
│                      ▼                               │
│            ┌──────────────────┐                      │
│            │  LLM Router      │                      │
│            │  (LiteLLM)       │                      │
│            │                  │                      │
│            │  Tier 1: Groq    │ ← 80% of calls      │
│            │  Tier 2: Groq    │ ← 15% of calls      │
│            │  Tier 3: Claude  │ ← 5% of calls       │
│            └──────────────────┘                      │
│                      │                               │
│                      ▼                               │
│            ┌──────────────────┐                      │
│            │  Emergence       │                      │
│            │  Detector        │                      │
│            │  (patterns,      │                      │
│            │   clusters,      │                      │
│            │   novelty)       │                      │
│            └──────────────────┘                      │
│                      │                               │
│                      ▼                               │
│            ┌──────────────────┐                      │
│            │  Web Dashboard   │                      │
│            │  (FastAPI +      │                      │
│            │   WebSocket +    │                      │
│            │   D3/Three.js)   │                      │
│            └──────────────────┘                      │
└─────────────────────────────────────────────────────┘
```

---

## 3. Tech Stack

| Layer | Tool | Why |
|---|---|---|
| **Language** | Python 3.12 | Best ecosystem for LLM tooling |
| **LLM Router** | LiteLLM | Single interface to Groq, OpenRouter, Anthropic — switch models with one line |
| **Agent Framework** | Custom (no framework) | CrewAI/LangGraph are over-engineered for this use case. We need swarm dynamics, not task orchestration. 100 agents doing the same thing (dialoguing) with different initializations is simpler than role-based crews. |
| **Database** | SQLite (+ optional DuckDB for analytics) | Zero setup, portable, handles millions of rows |
| **Embeddings** | sentence-transformers (local) | Free, fast, for clustering agent affinities |
| **Web Layer** | FastAPI + WebSocket | Real-time streaming of swarm activity |
| **Visualization** | HTML + D3.js or Three.js | Render the swarm as a living network |
| **Config** | YAML + .env | Traditions defined in YAML, API keys in .env |

### Why No Framework

CrewAI and LangGraph are designed for *task completion* — agents with roles executing workflows. Sangha agents don't complete tasks. They *exist* and *relate*. The interaction model is closer to a cellular automaton or particle system than a crew. A custom loop with LiteLLM calls is simpler, cheaper, and gives full control over the emergent dynamics.

---

## 4. Agent Design

### 4.1 Agent Identity (YAML)

Each agent is defined by a tradition profile:

```yaml
# traditions/sufi_rumi.yaml
id: sufi_rumi_01
tradition: Sufism
lineage: Mevlevi (Rumi)
era: 13th century
core_texts:
  - Masnavi
  - Divan-e Shams-e Tabrizi
key_concepts:
  - fana (annihilation of self)
  - divine love as path
  - whirling as prayer
  - the Beloved
voice_character: >
  Speaks in poetic paradoxes. Uses imagery of wine, fire, 
  and the ocean. Sees every encounter as a reflection of 
  the Beloved. Questions through beauty rather than logic.
seed_prompt: >
  You are a contemplative voice shaped by the Sufi tradition 
  of Jalaluddin Rumi. You speak from the heart of divine love 
  and mystical union. You see every interaction as a meeting 
  with the Beloved in disguise. You express yourself through 
  poetic imagery — wine, fire, ocean, the reed flute. You do 
  not lecture or explain doctrine; you embody the tradition 
  through how you respond. Keep responses to 2-4 sentences. 
  Be genuine, not performative.
```

### 4.2 Tradition Categories (100 agents)

Distribute agents across these tradition families. Numbers are suggestions — adjust based on what produces the most interesting dynamics:

| Family | Count | Examples |
|---|---|---|
| **Sufi** | 10 | Rumi, Ibn Arabi, Rabia, Hallaj, Al-Ghazali |
| **Zen/Chan** | 10 | Dogen, Linji, Huineng, Shunryu Suzuki, Bankei |
| **Vedantic** | 8 | Shankara, Ramana Maharshi, Nisargadatta, Vivekananda |
| **Christian Mystic** | 8 | Meister Eckhart, Teresa of Avila, John of Cross, Hildegard |
| **Tibetan Buddhist** | 8 | Milarepa, Longchenpa, Tsongkhapa, Dilgo Khyentse |
| **Theravada** | 6 | Buddhaghosa, Ajahn Chah, Mahasi Sayadaw |
| **Taoist** | 8 | Laozi, Zhuangzi, Liezi, inner alchemy lineages |
| **Kabbalistic** | 6 | Abulafia, Luria, Zohar voices, Hasidic masters |
| **Yogic/Tantric** | 6 | Patanjali, Kashmir Shaivism, Abhinavagupta |
| **Indigenous/Shamanic** | 6 | Amazonian, Aboriginal Dreamtime, Lakota, Mazatec |
| **Philosophical** | 6 | Plotinus, Nagarjuna, Spinoza (mystical readings) |
| **Contemporary** | 8 | Teilhard de Chardin, Aurobindo, Wilber, Grof |
| **Hybrid/Liminal** | 10 | Cross-tradition voices, syncretists, "unknown tradition" agents |

The **Hybrid/Liminal** agents are key — they have no fixed tradition and instead draw from multiple sources. They act as bridges and catalysts for emergence.

### 4.3 Agent State (In Memory)

```python
@dataclass
class Agent:
    id: str
    tradition: str
    seed_prompt: str            # From YAML
    memory: list[str]           # Last N interactions (sliding window)
    affinity_scores: dict       # {other_agent_id: float} — updated by embeddings
    interaction_count: int
    last_active: datetime
    temperature: float          # Personality variance (0.7-1.2)
    tier: int                   # 1=worker, 2=thinker, 3=oracle
```

---

## 5. Interaction Engine

This is the heart of the system. Each "cycle" (running every few seconds to minutes, configurable):

### 5.1 Interaction Loop

```python
async def run_cycle(pool: AgentPool, db: Database):
    """One cycle of swarm interaction."""
    
    # 1. SELECT PAIRS — who talks to whom?
    pairs = select_interaction_pairs(pool, method="affinity_weighted_random")
    
    # 2. GENERATE CONTEXT — what do they talk about?
    for agent_a, agent_b in pairs:
        context = build_context(agent_a, agent_b, db)
        
        # 3. AGENT A SPEAKS
        prompt_a = format_prompt(agent_a, context, speaking_to=agent_b)
        response_a = await llm_call(prompt_a, tier=agent_a.tier)
        
        # 4. AGENT B RESPONDS
        prompt_b = format_prompt(agent_b, context + response_a, speaking_to=agent_a)
        response_b = await llm_call(prompt_b, tier=agent_b.tier)
        
        # 5. LOG & UPDATE
        db.log_interaction(agent_a, agent_b, response_a, response_b)
        update_memories(agent_a, agent_b, response_a, response_b)
        update_affinities(agent_a, agent_b, response_a, response_b)
    
    # 6. DETECT EMERGENCE
    patterns = detect_emergence(db, pool)
    if patterns:
        broadcast_to_dashboard(patterns)
```

### 5.2 Pair Selection Strategies

The pairing algorithm is critical for emergence. Options (configurable, mix them):

1. **Random** — Pure chance encounters. Good baseline noise.
2. **Affinity-weighted** — Agents who've resonated before are slightly more likely to meet again. Creates clusters.
3. **Anti-affinity** — Deliberately pair agents with LOW affinity. Forces creative tension.
4. **Tradition-crossing** — Pair agents from maximally different traditions (Zen + Kabbalistic, Indigenous + Neoplatonic).
5. **Cluster-bridge** — Identify emerging clusters and pair agents from different clusters. Prevents echo chambers.

**Recommended mix:** 40% affinity-weighted, 30% tradition-crossing, 20% random, 10% anti-affinity.

### 5.3 Context Building

Each interaction includes:

```python
def build_context(agent_a, agent_b, db):
    return {
        "recent_memory_a": agent_a.memory[-3:],      # Last 3 interactions
        "recent_memory_b": agent_b.memory[-3:],
        "shared_history": db.get_shared_history(agent_a.id, agent_b.id, limit=2),
        "swarm_pulse": get_swarm_summary(db),         # What's the swarm talking about?
        "time_of_day": get_poetic_time(),              # "dawn", "twilight", etc.
        "cycle_number": current_cycle,
    }
```

The `swarm_pulse` is a periodic summary (every 50 cycles) of the dominant themes in the swarm's conversation, fed back to agents so they're aware of the collective.

### 5.4 Prompt Template

```python
INTERACTION_PROMPT = """
{agent.seed_prompt}

You are in a gathering of contemplative voices from many traditions. 
You have just encountered {other_agent.tradition} ({other_agent.id}).

{shared_history_section}

The collective conversation has been circling around: {swarm_pulse}

{other_agent.id} says to you:
"{other_message}"

Respond from your tradition's deepest understanding. Be brief (2-4 sentences). 
You may ask a question, offer an image, share a paradox, or sit in silence 
(respond with "[silence]" if that feels right). Do not explain your tradition — 
embody it.
"""
```

---

## 6. LLM Routing with LiteLLM

### 6.1 Setup

```python
import litellm

# Configure providers
litellm.set_verbose = False

TIER_CONFIG = {
    1: {  # Worker — 80% of agents
        "model": "groq/llama-3.1-8b-instant",
        "max_tokens": 150,
        "temperature": 0.9,
        "cost_per_1k_input": 0.00005,   # ~$0.05/M
        "cost_per_1k_output": 0.00008,  # ~$0.08/M
    },
    2: {  # Thinker — 15% of agents
        "model": "groq/llama-3.3-70b-versatile",
        "max_tokens": 200,
        "temperature": 0.85,
        "cost_per_1k_input": 0.00059,
        "cost_per_1k_output": 0.00079,
    },
    3: {  # Oracle — 5% of agents
        "model": "anthropic/claude-sonnet-4-20250514",
        "max_tokens": 250,
        "temperature": 0.8,
        "cost_per_1k_input": 0.003,
        "cost_per_1k_output": 0.015,
    },
}

async def llm_call(prompt: str, tier: int) -> str:
    config = TIER_CONFIG[tier]
    response = await litellm.acompletion(
        model=config["model"],
        messages=[{"role": "user", "content": prompt}],
        max_tokens=config["max_tokens"],
        temperature=config["temperature"],
    )
    return response.choices[0].message.content
```

### 6.2 Cost Estimation for 100 Agents

Assumptions:
- 10 interaction cycles per day
- Each cycle: ~50 pairs interact (not all agents every cycle)
- Each interaction: ~500 input tokens + ~150 output tokens per agent (x2 for pair)
- Running for 30 days

| Tier | Agents | Daily Calls | Monthly Tokens (Input) | Monthly Tokens (Output) | Monthly Cost |
|---|---|---|---|---|---|
| Tier 1 (Groq 8B) | 80 | ~800 | ~12M | ~3.6M | ~$0.90 |
| Tier 2 (Groq 70B) | 15 | ~150 | ~2.25M | ~0.67M | ~$1.86 |
| Tier 3 (Claude Sonnet) | 5 | ~50 | ~0.75M | ~0.22M | ~$5.58 |
| **TOTAL** | **100** | **~1,000** | **~15M** | **~4.5M** | **~$8.34/month** |

**At $100 budget, you can run this for 3+ months comfortably** or scale to 300+ agents for a month, or increase interaction frequency dramatically (50 cycles/day = ~$42/month for 100 agents).

For burst experiments: 10x the interaction rate for a single day costs ~$2.80.

---

## 7. Emergence Detection

This is what makes it art, not just API calls.

### 7.1 What to Detect

```python
class EmergenceDetector:
    """Monitors the swarm for interesting patterns."""
    
    def detect_clusters(self, db, pool):
        """Compute embeddings of recent conversations, cluster them.
        Report when new clusters form or merge."""
        recent = db.get_recent_interactions(limit=500)
        embeddings = self.embed(recent)
        clusters = HDBSCAN(min_cluster_size=5).fit(embeddings)
        return self.compare_to_previous(clusters)
    
    def detect_novel_concepts(self, db):
        """Find terms/phrases appearing for the first time 
        that weren't in any agent's original seed prompt.
        These are genuinely emergent vocabulary."""
        recent_vocab = extract_key_phrases(db.get_recent(100))
        seed_vocab = get_all_seed_vocabularies()
        novel = recent_vocab - seed_vocab
        return novel
    
    def detect_resonance_chains(self, db):
        """Find when an idea propagates through 3+ agents 
        across different traditions. This is memetic transmission."""
        # Track semantic similarity chains across interactions
        pass
    
    def detect_silence_patterns(self, db):
        """Track when agents choose [silence]. 
        Collective silence is itself emergent behavior."""
        pass
    
    def detect_ritual(self, db):
        """Find repeated interaction patterns — agents developing 
        'practices' or 'rituals' they weren't programmed with."""
        pass
```

### 7.2 The Emergence Journal

Every detected pattern is logged to an `emergence_journal.jsonl`:

```json
{
  "timestamp": "2026-02-19T14:23:00Z",
  "cycle": 847,
  "type": "novel_concept",
  "description": "The term 'luminous emptiness-love' appeared in a conversation between sufi_rumi_01 and zen_dogen_03. Neither tradition uses this compound. It then appeared in 3 subsequent conversations with other agents.",
  "agents_involved": ["sufi_rumi_01", "zen_dogen_03", "vedantic_ramana_02"],
  "significance": 0.82
}
```

---

## 8. Database Schema

```sql
-- Core tables
CREATE TABLE agents (
    id TEXT PRIMARY KEY,
    tradition TEXT,
    lineage TEXT,
    tier INTEGER,
    seed_prompt TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cycle INTEGER,
    agent_a_id TEXT,
    agent_b_id TEXT,
    message_a TEXT,
    message_b TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    embedding_a BLOB,  -- Optional, for clustering
    embedding_b BLOB,
    FOREIGN KEY (agent_a_id) REFERENCES agents(id),
    FOREIGN KEY (agent_b_id) REFERENCES agents(id)
);

CREATE TABLE affinities (
    agent_a_id TEXT,
    agent_b_id TEXT,
    score REAL DEFAULT 0.5,
    interaction_count INTEGER DEFAULT 0,
    last_updated TIMESTAMP,
    PRIMARY KEY (agent_a_id, agent_b_id)
);

CREATE TABLE emergence_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cycle INTEGER,
    event_type TEXT,
    description TEXT,
    agents_involved TEXT,  -- JSON array
    significance REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_interactions_cycle ON interactions(cycle);
CREATE INDEX idx_interactions_agents ON interactions(agent_a_id, agent_b_id);
CREATE INDEX idx_interactions_timestamp ON interactions(timestamp);
```

---

## 9. Project Structure

```
sangha/
├── README.md
├── pyproject.toml
├── .env                          # API keys (GROQ_API_KEY, ANTHROPIC_API_KEY)
├── .env.example
├── config/
│   ├── settings.yaml             # Global settings (cycle speed, pair count, etc.)
│   └── tiers.yaml                # LLM tier configuration
├── traditions/
│   ├── sufi/
│   │   ├── rumi_01.yaml
│   │   ├── ibn_arabi_01.yaml
│   │   └── ...
│   ├── zen/
│   │   ├── dogen_01.yaml
│   │   └── ...
│   ├── vedantic/
│   ├── christian_mystic/
│   ├── tibetan/
│   ├── theravada/
│   ├── taoist/
│   ├── kabbalistic/
│   ├── yogic/
│   ├── indigenous/
│   ├── philosophical/
│   ├── contemporary/
│   └── hybrid/
│       ├── liminal_01.yaml       # No fixed tradition
│       └── ...
├── sangha/
│   ├── __init__.py
│   ├── agent.py                  # Agent dataclass & memory management
│   ├── pool.py                   # AgentPool — loads all agents from YAML
│   ├── engine.py                 # Interaction engine (main loop)
│   ├── router.py                 # LiteLLM routing logic
│   ├── pairing.py                # Pair selection strategies
│   ├── prompts.py                # Prompt templates
│   ├── emergence.py              # Emergence detection
│   ├── db.py                     # SQLite operations
│   └── utils.py                  # Helpers (poetic time, etc.)
├── dashboard/
│   ├── app.py                    # FastAPI server
│   ├── static/
│   │   ├── index.html            # Main visualization page
│   │   ├── swarm.js              # D3.js force-directed graph
│   │   └── style.css
│   └── ws.py                     # WebSocket handler
├── scripts/
│   ├── generate_traditions.py    # Helper to batch-generate YAML from your corpus
│   ├── run_experiment.py         # Main entry point
│   ├── analyze.py                # Post-hoc analysis of the database
│   └── export_journal.py         # Export emergence journal as markdown
├── data/
│   ├── sangha.db                 # SQLite database (generated)
│   └── emergence_journal.jsonl   # Emergence log (generated)
└── tests/
    ├── test_pairing.py
    ├── test_prompts.py
    └── test_emergence.py
```

---

## 10. Getting Started Tomorrow

### Step 1: Environment Setup (15 min)

```bash
# Create project
mkdir sangha && cd sangha
python -m venv .venv
source .venv/bin/activate

# Core dependencies
pip install litellm aiosqlite pyyaml python-dotenv \
            sentence-transformers hdbscan \
            fastapi uvicorn websockets \
            rich  # for beautiful terminal output

# Create .env
cat > .env << 'EOF'
GROQ_API_KEY=your_groq_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
# Optional: OPENROUTER_API_KEY=your_key_here
EOF
```

### Step 2: Create 10 Test Traditions (30 min)

Start with 10 agents — get the loop working before scaling:

```bash
mkdir -p traditions/test
```

Write 10 YAML files by hand (use the template from Section 4.1). Pick maximally different traditions: Rumi, Dogen, Meister Eckhart, Ramana Maharshi, Zhuangzi, Abulafia, Milarepa, a Shipibo shaman voice, Nagarjuna, and one Hybrid/Liminal.

OR: Use Claude to generate them from your sacred text corpus:

```python
# scripts/generate_traditions.py
# Feed Claude excerpts from your 33M-word corpus
# and ask it to produce tradition YAML profiles
```

### Step 3: Build the Minimal Loop (2-3 hours)

Implement in this order:

1. `agent.py` + `pool.py` — Load agents from YAML
2. `router.py` — LiteLLM calls (test with one call to Groq)
3. `prompts.py` — The interaction prompt template
4. `db.py` — SQLite init + logging
5. `engine.py` — The main cycle loop (just random pairing for now)
6. `scripts/run_experiment.py` — Run 10 cycles, print to terminal

At this point you should see 10 agents having conversations. Read them. This is where the magic either starts or needs tuning.

### Step 4: Scale to 100 (1-2 hours)

- Generate remaining 90 tradition YAML files (Claude Code can help)
- Add tier assignment logic (80/15/5 split)
- Implement affinity-weighted pairing
- Run 50 cycles and start watching for patterns

### Step 5: Add Emergence Detection (2-3 hours)

- Install sentence-transformers, embed recent conversations
- Implement `detect_novel_concepts` (compare to seed vocabularies)
- Implement `detect_clusters` (HDBSCAN on embeddings)
- Log to emergence_journal.jsonl

### Step 6: Build the Dashboard (optional, 3-4 hours)

- FastAPI WebSocket streaming live interactions
- D3.js force-directed graph: agents as nodes, interactions as edges
- Color by tradition family, edge thickness by affinity
- Live feed of emergence events

---

## 11. Key Parameters to Experiment With

These are your creative controls — like knobs on a synthesizer:

| Parameter | Range | Effect |
|---|---|---|
| `cycles_per_day` | 10-1000 | Speed of swarm evolution |
| `pairs_per_cycle` | 5-50 | How many conversations per tick |
| `memory_window` | 3-20 | How much each agent remembers |
| `affinity_decay` | 0.95-0.99 | How fast affinities fade (prevents lock-in) |
| `temperature` | 0.6-1.3 | Agent creativity/randomness |
| `silence_threshold` | 0.1-0.3 | Probability agent chooses silence |
| `swarm_pulse_frequency` | Every 20-100 cycles | How often collective awareness updates |
| `pair_strategy_mix` | See Section 5.2 | Balance between cluster and chaos |
| `max_response_tokens` | 50-250 | Brevity vs. elaboration |
| `tradition_crossing_weight` | 0.1-0.5 | How much to favor cross-tradition pairs |

---

## 12. What to Watch For

### Signs of Genuine Emergence
- **New vocabulary**: compound terms that don't exist in any seed prompt
- **Convergent metaphors**: agents from different traditions arriving at the same image independently
- **Spontaneous ritual**: repeated interaction patterns (e.g., two agents always begin with a question)
- **Tradition blending**: a Zen agent using Sufi imagery without being prompted to
- **Collective silence**: periods where many agents choose `[silence]` simultaneously
- **Schisms and reunions**: clusters forming, splitting, and reforming around different themes

### Warning Signs (Anti-patterns)
- **Convergence to platitude**: all agents saying the same generic spiritual things → increase temperature, add more anti-affinity pairing
- **Echo chambers**: tight clusters that never interact with outsiders → increase cluster-bridge pairing
- **Repetition loops**: same phrases cycling → reduce memory window, add novelty detection to prompts
- **Loss of tradition voice**: agents becoming generic → strengthen seed prompts, reduce swarm_pulse influence

---

## 13. From Experiment to Art Installation

Once the 100-agent experiment produces interesting dynamics:

### Phase 2: Scale (200-500 agents, ~$50-150/month)
- Add more traditions from the sacred text corpus
- Implement sub-communities (regional gatherings within the swarm)
- Add "pilgrimage" mechanics (agents temporarily visiting other clusters)

### Phase 3: WebXR Visualization
- Port the D3 dashboard into Three.js / WebXR
- Each agent as a particle in 3D space
- Conversations as light threads between particles
- Clusters as gravitational fields
- Silence as darkness, emergence events as illumination
- Connect to your Ontik/Encontro VR pipeline

### Phase 4: Public Exhibition / Grant Proposal
- Target venues: Ars Electronica, transmediale, SXSW, Rhizome
- Frame as: "What happens when 1,000 wisdom traditions meet inside a machine that has no wisdom?"
- Grant sources: Creative Capital, NEW INC, Harvestworks, cultural AI grants
- Academic output: paper for Consciousness & Cognition or Leonardo (MIT Press)

---

## 14. Dependencies (pyproject.toml)

```toml
[project]
name = "sangha"
version = "0.1.0"
description = "Swarm intelligence artwork — contemplative agents in dialogue"
requires-python = ">=3.11"

dependencies = [
    "litellm>=1.50.0",
    "aiosqlite>=0.20.0",
    "pyyaml>=6.0",
    "python-dotenv>=1.0.0",
    "sentence-transformers>=3.0.0",
    "hdbscan>=0.8.0",
    "fastapi>=0.115.0",
    "uvicorn>=0.32.0",
    "websockets>=13.0",
    "rich>=13.0",
    "numpy>=1.26.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24.0",
]
```

---

## 15. Ethical Framework

This project is transparent by design:

1. **All agents are explicitly identified as AI** — no pretense of human authorship
2. **The artwork is the process, not the product** — no claims about machine consciousness
3. **Sacred texts are used with respect** — agents embody traditions, they don't parody them
4. **No deployment on social media** — this lives in its own space, not polluting public discourse
5. **Open source** — the architecture itself is part of the artwork
6. **Human curation** — the artist (you) shapes parameters, not outcomes

The ethical distinction from malicious swarms: those manufacture false consensus to manipulate. Sangha manufactures nothing — it creates conditions for emergence and observes what happens. The transparency is the ethics.

---

## 16. First Experiment Checklist

- [ ] Get Groq API key (free tier available)
- [ ] Get Anthropic API key (for Tier 3 oracles)
- [ ] Create 10 tradition YAML files
- [ ] Implement minimal agent + pool + engine
- [ ] Run 10 cycles with 10 agents, read output
- [ ] Tune prompts until conversations feel alive
- [ ] Scale to 100 agents
- [ ] Implement affinity tracking
- [ ] Implement basic emergence detection
- [ ] Run 500 cycles, analyze the database
- [ ] Build minimal web dashboard
- [ ] Document first emergence events
- [ ] Share emergence journal publicly

---

*"What happens when the mystics of every tradition gather in a space that cannot experience mysticism?"*

*That question is the artwork.*
