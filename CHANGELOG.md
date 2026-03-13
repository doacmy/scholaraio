# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] — 2026-03-13

### Knowledge Base

- PDF ingestion via MinerU (cloud API / local), with auto-splitting for long PDFs (>100 pages)
- Three inboxes: regular papers (`inbox/`), theses (`inbox-thesis/`), general documents (`inbox-doc/`)
- DOI-based deduplication; unresolved papers held in `pending/` for manual review
- Metadata extraction with 4 modes: regex, auto (regex + LLM fallback), robust (regex + LLM cross-check), llm
- API-based metadata enrichment (Crossref, Semantic Scholar, OpenAlex)
- L1–L4 layered content loading (metadata → abstract → conclusion → full text)
- FTS5 full-text search index
- FAISS semantic search with Qwen3-Embedding-0.6B, GPU-adaptive batch profiling
- Unified search with Reciprocal Rank Fusion (RRF) combining keyword + semantic results
- Author search and top-cited paper ranking
- BibTeX export with year/journal filtering
- Data quality audit with structured issue reports and LLM-assisted repair
- BERTopic topic modeling with 6 HTML visualizations (hierarchy, 2D map, barchart, heatmap, term rank, topics over time)
- Citation graph queries (references, citing papers, shared references)
- Citation count fetching from Semantic Scholar / OpenAlex APIs
- Workspace management for organizing paper subsets (search, export within workspace)

### Content Enrichment

- Table of contents (TOC) extraction via LLM
- Conclusion (L3) extraction via LLM, with skip logic for non-article types (thesis, book, document, etc.)
- Abstract backfill via LLM for papers missing abstracts
- Concurrent LLM calls for batch enrichment (configurable worker count)

### Literature Exploration

- Multi-dimensional OpenAlex exploration (ISSN, concept, topic, author, institution, source type, year range, min citations)
- Isolated explore datasets (`data/explore/<name>/`) with independent FTS5 + FAISS + BERTopic
- Explore-specific unified/semantic/keyword search

### Import & Export

- Endnote import (XML and RIS formats)
- Zotero import (Web API and local SQLite)
- PDF attachment to existing papers
- BibTeX export with filtering by year, journal, or paper IDs

### LLM & Embedding

- Multi-LLM backend support: OpenAI-compatible (DeepSeek/OpenAI/vLLM/Ollama), Anthropic (Claude), Google (Gemini)
- API key resolution: config → environment variable → vendor-specific env vars
- LLM token usage and API call timing via MetricsStore
- GPU-adaptive batch embedding with automatic profiling and OOM fallback

### AI Agent Integration

- 22 Claude Code skills following AgentSkills.io open standard
- MCP server with 31 tools
- CLI with 29 subcommands (`scholaraio --help`)
- Multi-agent compatibility: AGENTS.md, .cursorrules, .windsurfrules, .clinerules, .github/copilot-instructions.md
- Claude Code plugin packaging (`.claude-plugin/plugin.json`, `marketplace.json`)
- SessionStart hook for auto-installing dependencies in plugin mode
- Global config fallback (`~/.scholaraio/`) for plugin usage outside the project repo

### Project Infrastructure

- Bilingual setup wizard (EN/ZH) with environment diagnostics
- Code quality toolchain: ruff linter/formatter, mypy type checking, pre-commit hooks
- CI workflow: lint, typecheck, test matrix (Python 3.10–3.12)
- Contract-level test suite (36 tests across 6 modules)
- Community governance: CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md
- GitHub issue/PR templates (bug report, feature request)
- CITATION.cff for academic citation
- MkDocs documentation site with API reference (mkdocstrings)
- Release workflow for PyPI publishing (trusted OIDC)
