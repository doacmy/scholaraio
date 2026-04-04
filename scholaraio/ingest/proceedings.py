"""Proceedings detection and writeout helpers."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from scholaraio.index import build_proceedings_index
from scholaraio.papers import generate_uuid

_TITLE_KEYWORDS = (
    "proceedings of",
    "conference proceedings",
    "symposium proceedings",
    "workshop proceedings",
)

_TOC_PATTERNS = (
    "table of contents",
    "contents",
)

_DOI_RE = re.compile(r"10\.\d{4,}/[^\s)]+", re.IGNORECASE)
_HEADING_RE = re.compile(r"^(#{1,4})\s+(.+?)\s*$")
_TOP_LEVEL_HEADING_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)


def looks_like_proceedings_text(text: str) -> bool:
    lowered = text.lower()
    if any(keyword in lowered for keyword in _TITLE_KEYWORDS):
        return True
    if any(marker in lowered for marker in _TOC_PATTERNS) and len(set(_DOI_RE.findall(text))) >= 2:
        return True
    return len(set(_DOI_RE.findall(text))) >= 3


def detect_proceedings_from_md(md_path: Path, *, force: bool = False) -> tuple[bool, str]:
    """Detect whether a markdown file appears to represent a proceedings volume."""
    if force:
        return True, "manual_inbox"

    text = md_path.read_text(encoding="utf-8", errors="replace")
    lowered = text.lower()

    if any(keyword in lowered for keyword in _TITLE_KEYWORDS):
        return True, "title_keyword"
    if any(marker in lowered for marker in _TOC_PATTERNS):
        return True, "table_of_contents"
    if len(set(_DOI_RE.findall(text))) >= 3:
        return True, "multi_doi"
    return False, ""


def _slugify(text: str) -> str:
    cleaned = re.sub(r"[^\w\u4e00-\u9fff\s-]", "", text, flags=re.UNICODE)
    cleaned = re.sub(r"\s+", "-", cleaned.strip())
    return cleaned[:80].strip("-") or "untitled"


def _normalize_title_key(text: str) -> str:
    lowered = text.casefold()
    lowered = re.sub(r"\s+", " ", lowered).strip()
    return lowered


def _extract_volume_title(text: str, fallback: str) -> str:
    for match in _TOP_LEVEL_HEADING_RE.finditer(text):
        heading = match.group(1).strip()
        if "proceedings of" in heading.lower():
            return heading
    for match in _TOP_LEVEL_HEADING_RE.finditer(text):
        heading = match.group(1).strip()
        if heading and not heading.lower().endswith("editors"):
            return heading
    return fallback


def _extract_authors_and_abstract(chunk: str, title: str) -> tuple[list[str], str]:
    body = chunk.strip()
    if body.startswith(f"# {title}"):
        body = body[len(f"# {title}") :].lstrip()
    lines = [line.strip() for line in body.splitlines()]

    author_lines: list[str] = []
    abstract_lines: list[str] = []
    section = "authors"
    for line in lines:
        if not line:
            if section == "abstract" and abstract_lines:
                break
            if section == "authors" and author_lines:
                section = "affiliations"
            continue
        if line.startswith("#"):
            break
        if line.lower().startswith("abstract"):
            section = "abstract"
            abstract_lines.append(re.sub(r"^Abstract\.?\s*", "", line, flags=re.IGNORECASE).strip())
            continue
        if section == "abstract":
            if line.lower().startswith("keywords"):
                continue
            abstract_lines.append(line)
        elif section == "authors":
            author_lines.append(line)
        else:
            continue

    authors = [line for line in author_lines[:5] if line]
    abstract = "\n".join(line for line in abstract_lines if line).strip()
    return authors, abstract


def _parse_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```\w*\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def _extract_heading_outline(text: str) -> list[dict]:
    headings: list[dict] = []
    lines = text.splitlines()
    for line_no, line in enumerate(lines, start=1):
        match = _HEADING_RE.match(line)
        if not match:
            continue
        level = len(match.group(1))
        heading_text = match.group(2).strip()
        window = [candidate.strip() for candidate in lines[line_no : min(len(lines), line_no + 6)] if candidate.strip()]
        headings.append(
            {
                "level": level,
                "line": line_no,
                "text": heading_text,
                "normalized_text": _normalize_title_key(heading_text),
                "window": window,
            }
        )
    return headings


def _extract_contents_titles(text: str) -> list[str]:
    contents_heading = re.search(r"^#\s+Contents\s*$", text, flags=re.MULTILINE)
    if not contents_heading:
        return []

    first_paper_heading = re.search(r"^#\s+[^\n]+\n\n[^\n]+\n\nAbstract\.", text, flags=re.MULTILINE)
    end = first_paper_heading.start() if first_paper_heading else len(text)
    contents_block = text[contents_heading.end() : end]
    entries = [entry.strip().replace("\n", " ") for entry in re.split(r"\n\s*\n", contents_block) if entry.strip()]

    titles: list[str] = []
    for entry in entries:
        if entry.lower().startswith("author index"):
            continue
        cleaned = re.sub(r"\s+", " ", entry)
        cleaned = re.sub(r"\s+\d+\s+[A-Z].*$", "", cleaned).strip(" .")
        if cleaned:
            titles.append(cleaned)
    return titles


def _extract_contents_excerpt(text: str) -> str:
    contents_heading = re.search(r"^#\s+Contents\s*$", text, flags=re.MULTILINE)
    if not contents_heading:
        return ""

    lines = text[contents_heading.end() :].splitlines()
    excerpt: list[str] = []
    for line in lines:
        stripped = line.rstrip()
        if stripped.startswith("# ") and excerpt:
            break
        excerpt.append(stripped)
        if len(excerpt) >= 80:
            break
    return "\n".join(excerpt).strip()


def _build_split_candidates(text: str) -> dict:
    fallback_title = next((line.lstrip("# ").strip() for line in text.splitlines() if line.strip()), "untitled")
    contents_titles = _extract_contents_titles(text)
    return {
        "volume_title_hint": _extract_volume_title(text, fallback_title),
        "contents_excerpt": _extract_contents_excerpt(text),
        "contents_titles": contents_titles,
        "normalized_contents_titles": [_normalize_title_key(title) for title in contents_titles],
        "headings": _extract_heading_outline(text),
    }


def _slice_lines(lines: list[str], start_line: int, end_line: int) -> str:
    start_idx = max(0, start_line - 1)
    end_idx = min(len(lines), end_line)
    return "\n".join(lines[start_idx:end_idx]).strip()


def _papers_from_split_plan(text: str, plan: dict) -> list[dict]:
    lines = text.splitlines()
    papers: list[dict] = []
    for paper in plan.get("papers", []):
        title = paper["title"]
        chunk = _slice_lines(lines, int(paper["start_line"]), int(paper["end_line"]))
        if not chunk:
            continue
        if not chunk.lstrip().startswith("#"):
            chunk = f"# {title}\n\n{chunk}".strip()
        authors, abstract = _extract_authors_and_abstract(chunk, title)
        doi_match = _DOI_RE.search(chunk)
        papers.append(
            {
                "title": title,
                "authors": authors,
                "doi": doi_match.group(0) if doi_match else "",
                "abstract": abstract,
                "paper_type": "conference-paper",
                "markdown": chunk,
            }
        )
    return papers


def apply_proceedings_split_plan(proceeding_dir: Path, split_plan: dict | Path) -> Path:
    """Apply a human/agent-authored split plan to an existing proceedings directory."""
    if isinstance(split_plan, Path):
        plan = _parse_json(split_plan.read_text(encoding="utf-8"))
    else:
        plan = split_plan

    proceeding_md = proceeding_dir / "proceeding.md"
    if not proceeding_md.exists():
        raise FileNotFoundError(f"proceeding.md not found: {proceeding_md}")

    text = proceeding_md.read_text(encoding="utf-8", errors="replace")
    child_papers = _papers_from_split_plan(text, plan)
    papers_dir = proceeding_dir / "papers"
    papers_dir.mkdir(parents=True, exist_ok=True)

    for existing in papers_dir.iterdir():
        if existing.is_dir():
            shutil.rmtree(existing)
        else:
            existing.unlink()

    meta_path = proceeding_dir / "meta.json"
    proceeding_meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if plan.get("volume_title"):
        proceeding_meta["title"] = str(plan["volume_title"]).strip()
    proceeding_meta["child_paper_count"] = len(child_papers)
    proceeding_meta["split_status"] = "applied"
    meta_path.write_text(json.dumps(proceeding_meta, ensure_ascii=False, indent=2), encoding="utf-8")
    (proceeding_dir / "split_plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    for paper in child_papers:
        paper_dir = papers_dir / _slugify(paper["title"])
        paper_dir.mkdir(parents=True, exist_ok=True)
        paper_meta = {
            "id": generate_uuid(),
            "title": paper["title"],
            "authors": paper["authors"],
            "year": "",
            "journal": "",
            "doi": paper["doi"],
            "abstract": paper["abstract"],
            "paper_type": paper["paper_type"],
            "proceeding_id": proceeding_meta["id"],
            "proceeding_title": proceeding_meta["title"],
            "proceeding_dir": proceeding_dir.name,
        }
        (paper_dir / "meta.json").write_text(json.dumps(paper_meta, ensure_ascii=False, indent=2), encoding="utf-8")
        (paper_dir / "paper.md").write_text(paper["markdown"], encoding="utf-8")

    build_proceedings_index(proceeding_dir.parent, proceeding_dir.parent / "proceedings.db", rebuild=True)
    return proceeding_dir


def ingest_proceedings_markdown(
    proceedings_root: Path,
    md_path: Path,
    *,
    source_name: str = "",
) -> Path:
    """Write a proceedings volume shell under data/proceedings and wait for split review."""
    text = md_path.read_text(encoding="utf-8", errors="replace")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    fallback_title = lines[0].lstrip("# ").strip() if lines else md_path.stem
    split_candidates = _build_split_candidates(text)
    title = _extract_volume_title(text, fallback_title)

    proceeding_dir = proceedings_root / _slugify(title)
    suffix = 2
    while proceeding_dir.exists():
        proceeding_dir = proceedings_root / f"{_slugify(title)}-{suffix}"
        suffix += 1
    (proceeding_dir / "papers").mkdir(parents=True)

    proceeding_meta = {
        "id": generate_uuid(),
        "title": title,
        "source_file": source_name or md_path.name,
        "child_paper_count": 0,
        "split_status": "pending_review",
    }
    (proceeding_dir / "meta.json").write_text(json.dumps(proceeding_meta, ensure_ascii=False, indent=2), encoding="utf-8")
    (proceeding_dir / "proceeding.md").write_text(text, encoding="utf-8")
    (proceeding_dir / "split_candidates.json").write_text(
        json.dumps(split_candidates, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    build_proceedings_index(proceedings_root, proceedings_root / "proceedings.db", rebuild=True)
    return proceeding_dir
