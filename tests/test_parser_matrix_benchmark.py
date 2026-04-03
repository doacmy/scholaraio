from __future__ import annotations

from pathlib import Path

from scholaraio.config import Config
from scholaraio.ingest import parser_matrix_benchmark as bench


def test_slugify_value_handles_common_types():
    assert bench.slugify_value(True) == "true"
    assert bench.slugify_value(False) == "false"
    assert bench.slugify_value(300) == "300"
    assert bench.slugify_value(" referenced ") == "referenced"
    assert bench.slugify_value("RapidOCR + CUDA") == "rapidocr-cuda"


def test_make_run_slug_includes_parser_and_sorted_options():
    cfg = bench.RunConfig(
        parser="docling",
        options={
            "ocr_engine": "rapidocr",
            "enrich_formula": True,
            "image_export_mode": "referenced",
        },
    )
    assert bench.make_run_slug(cfg) == "docling__enrich_formula-true__image_export_mode-referenced__ocr_engine-rapidocr"


def test_expand_run_configs_builds_cross_product():
    spec = {
        "parser": "docling",
        "matrix": {
            "ocr_engine": ["rapidocr", "tesseract"],
            "enrich_formula": [False, True],
        },
    }
    runs = bench.expand_run_configs(spec)
    assert [r.parser for r in runs] == ["docling", "docling", "docling", "docling"]
    assert [r.options for r in runs] == [
        {"ocr_engine": "rapidocr", "enrich_formula": False},
        {"ocr_engine": "rapidocr", "enrich_formula": True},
        {"ocr_engine": "tesseract", "enrich_formula": False},
        {"ocr_engine": "tesseract", "enrich_formula": True},
    ]


def test_expand_run_configs_uses_explicit_name_when_given():
    spec = {
        "parser": "marker",
        "name": "marker_best",
        "options": {
            "force_ocr": True,
        },
    }
    runs = bench.expand_run_configs(spec)
    assert len(runs) == 1
    assert runs[0].name == "marker_best"


def test_make_output_dir_uses_index_and_slug(tmp_path: Path):
    cfg = bench.RunConfig(parser="pymupdf", options={"mode": "text"})
    out_dir = bench.make_output_dir(tmp_path, 3, cfg)
    assert out_dir == tmp_path / "03__pymupdf__mode-text"


def test_run_one_rejects_marker_parser(tmp_path: Path):
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    out_dir = tmp_path / "out"
    cfg = bench.RunConfig(parser="marker")

    result = bench.run_one(pdf, cfg, out_dir)

    assert result["ok"] is False
    assert result["error"] == "unsupported parser: marker"


def test_build_docling_command_includes_artifacts_path(tmp_path: Path):
    pdf = tmp_path / "paper.pdf"
    raw_dir = tmp_path / "raw"
    cmd = bench._build_docling_command(
        pdf,
        raw_dir,
        {
            "to": "md",
            "artifacts_path": "/home/lzmo/.cache/scholaraio/docling",
            "image_export_mode": "referenced",
        },
    )

    assert "--artifacts-path" in cmd
    assert "/home/lzmo/.cache/scholaraio/docling" in cmd
    assert "--image-export-mode" in cmd


def test_run_mineru_cloud_threads_cloud_model_version(tmp_path, monkeypatch):
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    md = tmp_path / "paper.md"
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()

    captured = {}

    monkeypatch.setattr(bench, "load_config", lambda: Config())

    class DummyResult:
        def __init__(self, md_path: Path):
            self.success = True
            self.error = None
            self.md_path = md_path

    monkeypatch.setattr(
        bench,
        "convert_pdf_cloud",
        lambda pdf_path, opts, api_key, cloud_url: (
            captured.setdefault("cloud_model_version", opts.cloud_model_version),
            DummyResult(raw_dir / "result.md"),
        )[1],
    )
    (raw_dir / "result.md").write_text("ok\n", encoding="utf-8")

    result = bench._run_mineru_cloud(
        pdf,
        md,
        raw_dir,
        bench.RunConfig(parser="mineru-cloud", options={"cloud_model_version": "vlm"}),
    )

    assert result["ok"] is True
    assert captured["cloud_model_version"] == "vlm"
