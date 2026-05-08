# 🚀 Research Agent Service

<div align="center">

**Production-Oriented LangGraph-Powered Web Research & Summarization Service**

![Version](https://img.shields.io/badge/version-V2-blue?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![Python](https://img.shields.io/badge/python-3.10+-blue?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?style=flat-square&logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-workflow-orange?style=flat-square)
![Status](https://img.shields.io/badge/status-active-brightgreen?style=flat-square)

</div>

---

## 📖 Overview

**Research Agent Service** is a standalone AI research backend designed to:

| Capability | Description |
|---|---|
| 🔍 **Discover** | Find web pages related to a user query |
| 🕷️ **Crawl** | Fetch and extract readable content from URLs |
| 📊 **Normalize** | Evaluate and score extracted sources |
| 🤖 **Summarize** | Generate grounded summaries using LLMs |
| 📦 **Respond** | Return structured research responses with metadata |

> The service is **intentionally separated** from the chatbot system. The chatbot becomes the interface layer; the research service becomes a specialized information retrieval and summarization engine.

```
Chatbot Service
      ↓
Research Agent Service
      ↓
Search → Crawl → Extract → Summarize
```

---

## 🔄 Pipeline at a Glance

```
┌─────────────┐    ┌──────────────────┐    ┌────────────────┐
│             │    │                  │    │                │
│  User Query │───▶│  Query Expansion │───▶│ Serper Search  │
│             │    │                  │    │                │
└─────────────┘    └──────────────────┘    └───────┬────────┘
                                                   │
                         ┌─────────────────────────▼───────────────────────┐
                         │             Federated Search Layer               │
                         │    URL Dedup · Safety Validation · Ranking       │
                         └─────────────────────────┬───────────────────────┘
                                                   │
                   ┌───────────────────────────────▼────────────────────────────┐
                   │                  Async Concurrent Crawl                     │
                   │          URL 1 ──┐                                          │
                   │          URL 2 ──┼── concurrent async (semaphore-bounded)   │
                   │          URL 3 ──┘                                          │
                   └───────────────────────────────┬────────────────────────────┘
                                                   │
                              ┌────────────────────▼────────────────────┐
                              │         Content Extraction               │
                              │  BeautifulSoup · readability-lxml · lxml │
                              └────────────────────┬────────────────────┘
                                                   │
                              ┌────────────────────▼────────────────────┐
                              │         Quality Assessment               │
                              │   high · medium · low · very_low · failed│
                              └────────────────────┬────────────────────┘
                                                   │
                              ┌────────────────────▼────────────────────┐
                              │           LLM Summarization              │
                              │      llm · fallback · none modes         │
                              └────────────────────┬────────────────────┘
                                                   │
                              ┌────────────────────▼────────────────────┐
                              │          Structured Response             │
                              │  trace_id · sources · metadata · summary │
                              └─────────────────────────────────────────┘
```

---

## 🧠 LangGraph Workflow

```
START
  │
  ▼
┌──────────────────────┐
│  create_search_plan  │  ← Query expansion + search strategy
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│    discover_urls     │  ← Serper API + normalization + ranking
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│     crawl_urls       │  ← Async concurrent + safety validation
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  summarize_sources   │  ← Grounded LLM summarization
└──────────┬───────────┘
           │
           ▼
          END
```

---

## 🏗️ Implementation Status

### ✅ V0 — Service Foundation
> _Core scaffolding and async baseline_

- [x] FastAPI service skeleton
- [x] LangGraph workflow
- [x] Configuration management
- [x] Structured logging
- [x] Environment management
- [x] Unit tests
- [x] Async architecture baseline

---

### ✅ V1 — Direct URL Crawling
> _Production crawling with safety and quality layers_

- [x] Direct URL crawling
- [x] Async concurrent crawling
- [x] Concurrency limiting (semaphore-based)
- [x] URL safety validation
- [x] Extraction quality scoring
- [x] Mocked crawler tests
- [x] Response metadata
- [x] LLM summarization fallback

---

### ✅ V2 — Search Discovery _(Current)_
> _Full query-driven discovery pipeline_

- [x] Search provider abstraction
- [x] Serper search provider
- [x] Query expansion
- [x] Search result normalization
- [x] Crawl-priority ranking
- [x] Federated search orchestration
- [x] LangGraph integration
- [x] Extraction stabilization

---

## ✨ Core Features

### 🔎 Search Discovery

Query-driven URL discovery with automatic deduplication and ranking:

```
query
  → query expansion
  → Serper search API
  → result normalization
  → URL deduplication
  → crawl-priority ranking
  → crawlable URLs
```

**Example request:**
```json
{
  "query": "latest AI agent frameworks"
}
```

---

### ⚡ Async Concurrent Crawling

Concurrent requests with bounded concurrency via semaphores:

```
URL 1 ┐
URL 2 ├── concurrent async crawling (HTTPX)
URL 3 ┘

CRAWLER_MAX_CONCURRENCY=3
```

---

### 🛡️ URL Safety System

Multi-layer URL validation before any crawl attempt:

| Check | Description |
|---|---|
| ✅ Allowed schemes | `http` and `https` only |
| ✅ Duplicate removal | Deduplication before crawl |
| ✅ Blocked domains | Configurable domain blocklist |
| ✅ Local target protection | Blocks `localhost`, `127.0.0.1`, `0.0.0.0` |

---

### 📊 Extraction Quality System

Graceful degradation instead of hard failure:

```
┌──────────┬─────────────────┬─────────────────────────────────┐
│  Level   │  Score Range    │  Behavior                       │
├──────────┼─────────────────┼─────────────────────────────────┤
│ high     │  0.8 – 1.0  ████████████ │  Full content, best signal     │
│ medium   │  0.6 – 0.8  ████████░░░░ │  Good partial content          │
│ low      │  0.3 – 0.6  ████░░░░░░░░ │  Partial recovery mode         │
│ very_low │  0.1 – 0.3  ██░░░░░░░░░░ │  Minimal signal, flagged       │
│ failed   │  0.0        ░░░░░░░░░░░░ │  Skipped, not catastrophic     │
└──────────┴─────────────────┴─────────────────────────────────┘
```

This enables: partial-content recovery · quality-aware summarization · better research robustness

---

### 🤖 LLM Summarization

| Mode | Description |
|---|---|
| `llm` | Full grounded summarization via OpenAI |
| `fallback` | Deterministic summary when LLM unavailable |
| `none` | Raw sources only, no summarization |

---

## 🧪 Usage Examples

### Query-Only Research

```bash
curl -X POST http://127.0.0.1:8000/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "latest AI agent frameworks"
  }'
```

### Direct URL Crawling

```bash
curl -X POST http://127.0.0.1:8000/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "summarize this article",
    "urls": [
      "https://example.com"
    ]
  }'
```

### Example Response

```json
{
  "trace_id": "uuid",
  "query": "latest AI agent frameworks",
  "summary_mode": "llm",
  "source_count": 5,
  "failed_source_count": 1,
  "summary": "...",
  "sources": [
    {
      "url": "https://example.com",
      "title": "Example",
      "status_code": 200,
      "word_count": 500,
      "extraction_quality": "medium",
      "extraction_quality_score": 0.7
    }
  ]
}
```

---

## 📁 Project Structure

```
research-agent-service/
│
├── app/
│   ├── api/            ← FastAPI routes and request handling
│   ├── core/           ← Config, logging, environment
│   ├── crawler/        ← Async crawling + safety validation
│   ├── graph/          ← LangGraph workflow nodes and state
│   ├── llm/            ← Summarization and LLM integration
│   ├── schemas/        ← Pydantic request/response models
│   └── search/         ← Search providers and orchestration
│
├── tests/              ← Pytest + RESPX mocked tests
├── requirements.txt
├── .env
├── pytest.ini
└── README.md
```

---

## 🧰 Tech Stack

### 🖥️ Backend
![FastAPI](https://img.shields.io/badge/-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/-LangGraph-orange?style=flat-square)
![Pydantic](https://img.shields.io/badge/-Pydantic-e92063?style=flat-square)
![AsyncIO](https://img.shields.io/badge/-AsyncIO-3776AB?style=flat-square&logo=python&logoColor=white)
![HTTPX](https://img.shields.io/badge/-HTTPX-0098FF?style=flat-square)

### 🌐 Crawling & Extraction
![BeautifulSoup](https://img.shields.io/badge/-BeautifulSoup4-4B8BBE?style=flat-square)
![readability](https://img.shields.io/badge/-readability--lxml-lightgrey?style=flat-square)
![lxml](https://img.shields.io/badge/-lxml-4B8BBE?style=flat-square)

### 🧠 AI Layer
![OpenAI](https://img.shields.io/badge/-OpenAI_API-412991?style=flat-square&logo=openai&logoColor=white)
![Serper](https://img.shields.io/badge/-Serper_API-green?style=flat-square)

### 🧪 Testing
![Pytest](https://img.shields.io/badge/-Pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)
![RESPX](https://img.shields.io/badge/-RESPX-lightgrey?style=flat-square)

---

## 🏛️ Engineering Principles

```
01. SERVICE SEPARATION    Research logic isolated from chatbot orchestration
02. PROVIDER ABSTRACTION  Search providers are interchangeable by design
03. ASYNC-FIRST           Crawler built around async I/O from the ground up
04. GRACEFUL DEGRADATION  Weak extraction = low confidence, not failure
05. PRODUCTION-ORIENTED   Config, logging, testing, observability first-class
```

---

## ⚠️ Current Limitations (V2)

The current V2 system intentionally does **not** yet include:

- ❌ Browser automation (Playwright)
- ❌ JavaScript-rendered page crawling
- ❌ Proxy rotation / CAPTCHA handling
- ❌ Advanced anti-bot bypass
- ❌ Background job queues
- ❌ Streaming summarization
- ❌ Content semantic ranking
- ❌ Reflection / agentic loops

These are planned for later stages.

---

## 🗺️ Roadmap

```
V3 ── Summarization Layer ────────────────────────────────────────────── 📄
       Content relevance scoring · Citation formatting
       Hallucination guardrails · Retry/fallback policies

V4 ── Production Reliability ─────────────────────────────────────────── 🛡️
       OpenTelemetry · Metrics · Security hardening
       CI/CD · Docker production profiles

V5 ── Chatbot Integration ────────────────────────────────────────────── 🔌
       REST integration · RabbitMQ/event integration
       Streaming research updates · Cross-service tracing

V6 ── Advanced Agentic Research ──────────────────────────────────────── 🤖
       Research planner · Query decomposition
       Reflection loops · Conflict detection
       Long-running research jobs · CPU/process-pool execution
```

---

## 🎯 Philosophy

> This project intentionally avoids **"AI magic first."**

The system is being built from first principles:

```
Reliable retrieval
  → Structured extraction
    → Quality assessment
      → Grounded summarization
        → Agentic behavior later
```

The goal is to build a **production-grade research system**, not a demo chatbot.

---

## 📄 License

[MIT License](LICENSE)