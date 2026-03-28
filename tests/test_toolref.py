from __future__ import annotations

import json

from scholaraio.toolref import (
    _build_bioinformatics_manifest,
    _build_openfoam_manifest,
    _has_local_docs,
    _normalize_program_filter,
    _parse_manifest_html,
)


def test_normalize_program_filter_for_qe():
    assert _normalize_program_filter("qe", "pw") == "pw.x"
    assert _normalize_program_filter("qe", "ph.x") == "ph.x"


def test_normalize_program_filter_for_non_qe():
    assert _normalize_program_filter("openfoam", "simpleFoam") == "simplefoam"
    assert _normalize_program_filter("bioinformatics", "samtools") == "samtools"


def test_build_openfoam_manifest_uses_requested_version():
    manifest = _build_openfoam_manifest("2312")
    assert manifest
    assert all("page_name" in item for item in manifest)
    assert any("/2312/" in item["url"] for item in manifest if "doc.openfoam.com" in item["url"])


def test_build_bioinformatics_manifest_contains_multiple_subtools():
    manifest = _build_bioinformatics_manifest("2026-03-curated")
    programs = {item["program"] for item in manifest}
    assert {"blastn", "minimap2", "samtools", "bcftools", "mafft", "iqtree", "esmfold"} <= programs


def test_parse_manifest_html_extracts_main_text(tmp_path):
    html_path = tmp_path / "page.html"
    meta_path = tmp_path / "page.json"

    html_path.write_text(
        """
        <html>
          <body>
            <main>
              <h1>simpleFoam</h1>
              <p>Steady-state incompressible solver.</p>
              <pre><code>simpleFoam -case motorBike</code></pre>
            </main>
          </body>
        </html>
        """,
        encoding="utf-8",
    )
    meta_path.write_text(
        json.dumps(
            {
                "program": "simpleFoam",
                "section": "solver",
                "page_name": "openfoam/simpleFoam",
                "title": "simpleFoam",
            }
        ),
        encoding="utf-8",
    )

    records = _parse_manifest_html(html_path)

    assert len(records) == 1
    record = records[0]
    assert record["page_name"] == "openfoam/simpleFoam"
    assert "Steady-state incompressible solver." in record["content"]
    assert "simpleFoam -case motorBike" in record["content"]


def test_has_local_docs_for_manifest_html(tmp_path, monkeypatch):
    from scholaraio import toolref as mod

    monkeypatch.setattr(mod, "_DEFAULT_TOOLREF_DIR", tmp_path)
    pages_dir = tmp_path / "openfoam" / "2312" / "pages"
    pages_dir.mkdir(parents=True)
    assert not _has_local_docs("openfoam", "2312")

    (pages_dir / "001-openfoam-simpleFoam.html").write_text("<html></html>", encoding="utf-8")
    assert not _has_local_docs("openfoam", "2312")

    manifest = _build_openfoam_manifest("2312")
    for idx, item in enumerate(manifest, start=1):
        (pages_dir / f"{idx:03d}-{item['page_name'].replace('/', '-')}.html").write_text("<html></html>", encoding="utf-8")
    assert _has_local_docs("openfoam", "2312")
