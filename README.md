# 🧠 agent-hindsight

> **Temporal long-term memory engine with recency decay and FTS5 ranking for AI coding agents.**  
> Give your AI assistants persistent, continuous memory across sessions without running an external vector database.

[![PyPI version](https://img.shields.io/badge/pypi-0.1.0-blue.svg)](https://pypi.org/project/agent-hindsight/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.9+](https://img.shields.io/badge/python-3.9+-brightgreen.svg)](https://python.org)

---

## 🎯 The Problem

Standard AI coding agents (Claude Code, Cursor, Copilot, Aider) start with amnesia every session:
* They forget critical architectural decisions made yesterday.
* Context compaction wipes away hard-earned debugging solutions and configuration rules.
* Heavy vector databases (Pinecone, Milvus, Qdrant cluster) are complex to configure and lack temporal awareness.

## 💡 The Solution

`agent-hindsight` stores facts locally in SQLite using **FTS5 full-text search coupled with Ebbinghaus exponential recency decay ($e^{-\lambda t}$)**.

Each memory score is calculated from:
$$\text{Score} = (\text{BM25 Match}) \times \left(\frac{\text{Importance}}{5}\right) \times e^{-0.005 \cdot \text{age}_{\text{hours}}}$$

* High-importance facts stay accessible for months.
* Trivial facts naturally fade over time.
* Fast keyword matching returns answers in **under 2 milliseconds**.

---

## 🚀 Installation

```bash
pip install agent-hindsight
```

---

## 💻 CLI Usage

### Retain a Fact
```bash
hindsight retain "Production Postgres runs on port 5432 with replica on 5433" -c database -i 8
hindsight retain "Use pnpm instead of npm for all frontend workspace packages" -c architecture -i 9
```

### Recall Facts
```bash
# Query memories matching terms
hindsight recall "postgres"

# Filter by category
hindsight recall -c database
```

### System Reflection
Synthesize overall knowledge anchors and top category clusters:
```bash
hindsight reflect
```

---

## 🐍 Python SDK Usage

```python
from agent_hindsight import retain, recall, reflect

# Retain architectural fact
retain("Auth service uses RS256 JWT tokens with 15-minute expiration", category="auth", importance=9)

# Recall relevant facts for active prompt
memories = recall("JWT expiration", limit=3)
for m in memories:
    print(f"[{m['category']} | Score: {m['score']}] {m['fact']}")

# Consolidate knowledge
summary = reflect()
print(f"Total stored memories: {summary['total_memories']}")
```

---

## 🧪 Testing

```bash
python3 -m unittest discover tests
```

---

## 📄 License

MIT © [Ayyappa Pravin](https://github.com/apravint)
