<div align="center">

<!-- TODO: Replace with actual logo when available -->
<!-- <img src="docs/assets/logo.png" width="200" alt="ScholarAIO Logo"> -->

# ScholarAIO

**Scholar All-In-One — a knowledge infrastructure for AI agents.**

[English](README.md) | [中文](README_CN.md)

[![GitHub stars](https://img.shields.io/github/stars/ZimoLiao/scholaraio?style=social)](https://github.com/ZimoLiao/scholaraio/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Claude Code Skills](https://img.shields.io/badge/Claude_Code_Skills-ScholarAIO-purple.svg)](.claude/skills/)

</div>

---

Your coding agent already reads code, writes code, and runs experiments. ScholarAIO gives it a structured research workspace, so the same agent can search literature, cross-check results against papers, use scientific software more accurately, and drive the full research loop from one terminal.

What makes it different:

- Your papers become a searchable, reusable knowledge base for the same agent that writes your code.
- Scientific software questions can be grounded in official docs at runtime instead of prompt guesswork.
- The system is designed to keep growing as users need more scientific tools and workflows.

<div align="center">
  <img src="docs/assets/scholaraio.gif" width="900" alt="ScholarAIO natural-language research workflow">
</div>

ScholarAIO gives an AI coding agent a real research workspace. It lets the agent interact in natural language, ground on papers and persistent notes, use scientific tools more accurately, write and run code, validate results against the literature, and turn the work into structured scientific writing.

<div align="center">
  <img src="docs/assets/scholaraio-architecture-v1.3.0.png" width="900" alt="ScholarAIO architecture: human, agent, scientific context, tool layer, and compute/outputs">
</div>

## Quick Start

The default and best way to try ScholarAIO is simple: install it, configure it once, and open this repository directly with your coding agent.

```bash
git clone https://github.com/ZimoLiao/scholaraio.git
cd scholaraio
pip install -e ".[full]"
scholaraio setup
```

Then open the repository in Codex, Claude Code, or another supported agent. In this mode, your agent gets the full packaged experience: bundled instructions, local skills, CLI, and the complete codebase context. For plugins, global skill registration, and other setup paths, see [`docs/getting-started/agent-setup.md`](docs/getting-started/agent-setup.md).

## What It Does

|  | Feature | Details |
|--|---------|---------|
| **PDF Parsing** | Deep structure extraction | Prefer [MinerU](https://github.com/opendatalab/MinerU) or [Docling](https://github.com/docling-project/docling) for structured Markdown. If neither is available, ScholarAIO falls back to PyMuPDF text extraction. With MinerU, local parsing follows `chunk_page_limit` (default: >100 pages), while cloud parsing also respects the documented `>600 pages` and `>200MB` limits and estimates a safe chunk size when only the file-size limit is exceeded |
| **Not Just Papers** | Any document goes in | Journal articles, theses, patents, technical reports, standards, lecture notes — four inboxes with tailored metadata handling |
| **Hybrid Search** | Keyword + semantic fusion | Keyword + semantic embeddings → RRF ranking |
| **Topic Discovery** | Auto-clustering | BERTopic + 6 interactive HTML visualizations — works on both your library and explore datasets |
| **Literature Exploration** | Multi-dimensional discovery | OpenAlex with 9 filter dimensions (journal, concept, author, institution, keyword, source type, year, citations, work type) → embed → cluster → search |
| **Citation Graph** | References & impact | Forward/backward citations, shared references across your library |
| **Layered Reading** | Read at the depth you need | L1 metadata → L2 abstract → L3 conclusion → L4 full text |
| **Multi-Source Import** | Bring your existing library | Endnote XML/RIS, Zotero (API + SQLite, with collection → workspace mapping), PDF, Markdown — more sources planned |
| **Workspaces** | Organize for projects | Paper subsets with scoped search and BibTeX export |
| **Multi-Format Export** | BibTeX, RIS, Markdown, DOCX | Export your library or workspace in any format — ready for Zotero, Endnote, manuscript submission, or sharing |
| **Persistent Notes** | Cross-session memory | Agent analysis is saved per-paper (`notes.md`). Revisiting a paper reuses prior findings instead of re-reading the full text — saves tokens and avoids redundant work |
| **Research Insights** | Reading behavior analytics | Search hot keywords, most-read papers, reading trends, and semantic neighbor recommendations for papers you haven't read yet |
| **Federated Discovery** | Search across silos | Search your main library, explore silos, and arXiv in one command; pull arXiv PDFs directly into the ingest pipeline |
| **AI-for-Science Runtime** | Use scientific software more accurately | Agents can look up official tool interfaces at runtime through `toolref`, which already covers Quantum ESPRESSO, LAMMPS, GROMACS, OpenFOAM, and curated bioinformatics tools |
| **Extensible Tool Onboarding** | Add the next tool users need | ScholarAIO is designed to keep expanding beyond the first five scientific domains, with a dedicated onboarding workflow for bringing in additional user-requested tools |
| **Academic Writing** | AI-assisted drafting | Literature review, paper sections, citation check, rebuttal, gap analysis — every claim traceable to your own library |

## Beyond Paper Management

ScholarAIO parses PDFs into clean Markdown with accurate LaTeX and figure attachments. This means your coding agent doesn't just *read* papers — it can:

- **Reproduce methods** — read an algorithm description, write the implementation, run it
- **Verify claims** — extract data from figures and tables, compute independently, cross-check
- **Explore formulas** — pick up where a derivation leaves off, test boundary cases numerically
- **Visualize results** — plot data from papers alongside your own experiments

The knowledge base is the foundation; what your agent builds on top of it is open-ended.

## Works With Your Agent

ScholarAIO is designed to be **agent-agnostic**, but not every agent exposes the same installation surface. Some work best by opening this repository directly; others are better through plugins.

| Agent / IDE | Open this repo directly | Reuse from another project |
|-------------|-------------------------|-----------------------------|
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | `CLAUDE.md` + `.claude/skills/` | Claude plugin marketplace |
| [Codex](https://openai.com/codex) / OpenClaw | `AGENTS.md` + `.agents/skills/` | Symlink skills into `~/.agents/skills/` |
| [Cline](https://github.com/cline/cline) | `.clinerules` + `.claude/skills/` | CLI + skills |
| [Cursor](https://cursor.sh) | `.cursorrules` | CLI + skills |
| [Windsurf](https://codeium.com/windsurf) | `.windsurfrules` | CLI + skills |
| [GitHub Copilot](https://github.com/features/copilot) | `.github/copilot-instructions.md` | CLI + skills |

Skills follow the open [AgentSkills.io](https://agentskills.io) standard, and `.agents/skills/` is a symlink to `.claude/skills/` for cross-agent discovery.

**Migrating from existing tools?** Import directly from Endnote (XML/RIS) and Zotero (Web API or local SQLite) — your PDFs, metadata, and references come along. More import sources are on the roadmap.

## Configuration

ScholarAIO works with a minimal setup and grows from there.

- `scholaraio setup` walks you through the basics.
- An LLM API key is optional but recommended for metadata extraction, enrichment, and deeper academic discussion.
- A MinerU token is optional; without it, ScholarAIO can still fall back to Docling or PyMuPDF for PDF parsing.
- `scholaraio setup check` shows what is installed, what is optional, and what is missing.

Full setup and configuration details → [`docs/getting-started/agent-setup.md`](docs/getting-started/agent-setup.md), [`config.yaml`](config.yaml)

## Agent First, CLI Available

ScholarAIO is designed to work best through an AI coding agent, but the CLI is available for scripting, inspection, and quick queries. For a current command reference aligned with the code, see [`docs/guide/cli-reference.md`](docs/guide/cli-reference.md).

## Project Structure

```
scholaraio/          # Python package — CLI and all core modules
  ingest/            #   PDF parsing + metadata extraction pipeline
  sources/           #   External source adapters (arXiv / Endnote / Zotero)

.claude/skills/      # Agent skills (AgentSkills.io format)
.agents/skills/      # ↑ symlink for cross-agent discovery
data/papers/         # Your paper library (gitignored)
data/proceedings/    # Proceedings library (gitignored)
data/inbox/          # Drop PDFs here for ingestion
data/inbox-proceedings/ # Drop proceedings volumes here for dedicated ingest
```

Proceedings only enter the proceedings workflow from `data/inbox-proceedings/`. Regular `data/inbox/` items stay on the normal paper/document path unless you move them into the dedicated proceedings inbox explicitly.

Full module reference → [`CLAUDE.md`](CLAUDE.md) or [`AGENTS.md`](AGENTS.md)

## Citation

If you use ScholarAIO in your research, please cite:

```bibtex
@software{scholaraio,
  author = {Liao, Zi-Mo},
  title = {ScholarAIO: AI-Native Research Terminal},
  year = {2026},
  url = {https://github.com/ZimoLiao/scholaraio},
  license = {MIT}
}
```

## License

[MIT](LICENSE) © 2026 Zi-Mo Liao
