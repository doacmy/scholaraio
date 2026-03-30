"""Shared arXiv Atom API helpers used by CLI, ingest, and federated search."""

from __future__ import annotations

import logging
import re
from html import unescape
from urllib.parse import urlparse

import defusedxml.ElementTree as ET

_log = logging.getLogger(__name__)

_ARXIV_API_URL = "https://export.arxiv.org/api/query"
_ARXIV_NEW_ID_RE = re.compile(r"^\d{4}\.\d{4,5}$")
_ARXIV_OLD_ID_RE = re.compile(r"^[a-z\-]+(?:\.[A-Z]{2})?/\d{7}$", re.IGNORECASE)


def _user_agent() -> str:
    try:
        from scholaraio import __version__
    except Exception:
        __version__ = "unknown"
    return f"scholaraio/{__version__} (https://github.com/ZimoLiao/scholaraio)"


_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}


def normalize_arxiv_ref(ref: str) -> str:
    """Normalize an arXiv identifier / URL to a canonical ID without version suffix.

    Args:
        ref: Bare arXiv ID, ``arXiv:<id>``, or ``arxiv.org/abs|pdf/...`` URL.

    Returns:
        Canonical arXiv ID without version suffix, or an empty string if invalid.
    """
    raw = (ref or "").strip()
    if not raw:
        return ""

    lowered = raw.lower()
    if lowered.startswith("arxiv:"):
        raw = raw.split(":", 1)[1].strip()
    elif lowered.startswith("http://") or lowered.startswith("https://"):
        parsed = urlparse(raw)
        path = parsed.path.strip("/")
        if path.startswith("abs/"):
            raw = path[len("abs/") :]
        elif path.startswith("pdf/"):
            raw = path[len("pdf/") :]
            if raw.lower().endswith(".pdf"):
                raw = raw[:-4]
        else:
            return ""

    raw = raw.strip().rstrip("/")
    raw = re.sub(r"v\d+$", "", raw, flags=re.IGNORECASE)
    if _ARXIV_NEW_ID_RE.fullmatch(raw) or _ARXIV_OLD_ID_RE.fullmatch(raw):
        return raw
    return ""


def _parse_entry(entry: ET.Element) -> dict:
    title_el = entry.find("atom:title", _NS)
    title = (title_el.text or "").strip().replace("\n", " ") if title_el is not None else ""

    summary_el = entry.find("atom:summary", _NS)
    abstract = (summary_el.text or "").strip().replace("\n", " ") if summary_el is not None else ""

    year = ""
    pub_el = entry.find("atom:published", _NS)
    if pub_el is not None and pub_el.text:
        year = pub_el.text[:4]

    authors: list[str] = []
    for author_el in entry.findall("atom:author", _NS):
        name_el = author_el.find("atom:name", _NS)
        if name_el is not None and name_el.text:
            authors.append(name_el.text)

    arxiv_id = ""
    id_el = entry.find("atom:id", _NS)
    if id_el is not None and id_el.text:
        arxiv_id = id_el.text.strip().split("/abs/")[-1]

    doi = ""
    doi_el = entry.find("arxiv:doi", _NS)
    if doi_el is not None and doi_el.text:
        doi = doi_el.text.strip()

    return {
        "title": title,
        "authors": authors,
        "year": year,
        "abstract": abstract,
        "arxiv_id": arxiv_id,
        "doi": doi,
    }


def _query_arxiv_api(params: dict[str, str | int]) -> list[dict]:
    import requests

    try:
        resp = requests.get(_ARXIV_API_URL, params=params, headers={"User-Agent": _user_agent()}, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        _log.warning("arXiv API 不可用: %s", e)
        return []

    try:
        root = ET.fromstring(resp.text)
    except Exception as e:
        _log.warning("arXiv XML 解析失败: %s", e)
        return []

    return [_parse_entry(entry) for entry in root.findall("atom:entry", _NS)]


def _fetch_arxiv_abs_page(arxiv_id: str) -> dict:
    """Fetch metadata from the official arXiv abstract page as a fallback."""
    import requests

    url = f"https://arxiv.org/abs/{arxiv_id}"
    try:
        resp = requests.get(url, headers={"User-Agent": _user_agent()}, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        _log.warning("arXiv abs 页面不可用: %s", e)
        return {}

    html = resp.text
    meta_pairs = re.findall(r'<meta\s+name="([^"]+)"\s+content="([^"]*)"', html, flags=re.IGNORECASE)
    if not meta_pairs:
        return {}

    meta_map: dict[str, list[str]] = {}
    for name, content in meta_pairs:
        meta_map.setdefault(name.lower(), []).append(unescape(content).strip())

    title = (meta_map.get("citation_title") or [""])[0]
    authors = [a for a in meta_map.get("citation_author", []) if a]
    date = (meta_map.get("citation_date") or [""])[0]
    abstract = (meta_map.get("citation_abstract") or [""])[0]
    page_arxiv_id = (meta_map.get("citation_arxiv_id") or [""])[0]
    doi = (meta_map.get("citation_doi") or [""])[0]

    if not any([title, authors, date, abstract, page_arxiv_id, doi]):
        return {}

    year = ""
    if date:
        year = date[:4]

    return {
        "title": title,
        "authors": authors,
        "year": year,
        "abstract": abstract,
        "arxiv_id": page_arxiv_id or arxiv_id,
        "doi": doi,
    }


def get_arxiv_paper(arxiv_ref: str) -> dict:
    """Fetch authoritative metadata for a single arXiv paper via the Atom API.

    Args:
        arxiv_ref: arXiv ID or URL.

    Returns:
        Simplified paper dict with keys ``title``, ``authors``, ``year``,
        ``abstract``, ``arxiv_id``, ``doi``. Returns an empty dict on failure.
    """
    canonical_id = normalize_arxiv_ref(arxiv_ref)
    if not canonical_id:
        return {}
    results = _query_arxiv_api({"id_list": canonical_id})
    if results:
        return results[0]
    return _fetch_arxiv_abs_page(canonical_id)


def search_arxiv(query: str, top_k: int = 10) -> list[dict]:
    """Query the arXiv Atom API and return a list of simplified paper dicts.

    Args:
        query: Free-text search query.
        top_k: Maximum number of results to return.

    Returns:
        List of dicts with keys: title, authors, year, abstract, arxiv_id, doi.
        Returns an empty list on network failure or XML parse error.
    """
    params: dict[str, str | int] = {"search_query": f"all:{query}", "max_results": top_k, "sortBy": "relevance"}
    return _query_arxiv_api(params)
