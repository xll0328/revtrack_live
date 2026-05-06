from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_paper_citations.py"
SPEC = importlib.util.spec_from_file_location("audit_paper_citations", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
audit_paper_citations = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit_paper_citations)


def write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_citation_audit_passes_for_complete_bibliography(tmp_path: Path) -> None:
    paper_dir = tmp_path / "paper"
    write_file(
        paper_dir / "main.tex",
        r"""
\documentclass{article}
\begin{document}
\citep{peerread,fever}
\input{sections/related}
\bibliography{refs}
\end{document}
""",
    )
    write_file(paper_dir / "sections/related.tex", r"\citet[see][]{nlpeer} % \citep{ignored}")
    write_file(
        paper_dir / "refs.bib",
        r"""
@inproceedings{peerread,
  author = {A. Author},
  title = {PeerRead},
  booktitle = {ACL},
  year = {2018},
  doi = {10.1/test}
}
@inproceedings{fever,
  author = {B. Author},
  title = {FEVER},
  booktitle = {NAACL},
  year = {2018},
  url = {https://example.com}
}
@misc{nlpeer,
  author = {C. Author},
  title = {NLPeer},
  year = {2023},
  eprint = {1234.5678}
}
""",
    )
    write_file(paper_dir / "main.log", "Output written on main.pdf\n")

    report = audit_paper_citations.audit_citations(
        paper_dir=paper_dir,
        bib_path=paper_dir / "refs.bib",
        log_path=paper_dir / "main.log",
    )

    assert report["status"] == "pass"
    assert report["ok"] is True
    assert report["citation_occurrences"] == 3
    assert report["cited_keys"] == ["fever", "nlpeer", "peerread"]
    assert report["unused_bib_keys"] == []
    assert report["missing_bib_keys"] == []


def test_citation_audit_blocks_missing_bib_key_and_required_fields(tmp_path: Path) -> None:
    paper_dir = tmp_path / "paper"
    write_file(paper_dir / "main.tex", r"\citep{known,missing}\bibliography{refs}")
    write_file(
        paper_dir / "refs.bib",
        r"""
@inproceedings{known,
  author = {A. Author},
  title = {Known},
  year = {2026}
}
""",
    )
    write_file(paper_dir / "main.log", "Output written on main.pdf\n")

    report = audit_paper_citations.audit_citations(
        paper_dir=paper_dir,
        bib_path=paper_dir / "refs.bib",
        log_path=paper_dir / "main.log",
    )

    assert report["status"] == "blocker"
    assert report["missing_bib_keys"] == ["missing"]
    assert report["missing_required_fields"] == [
        {"key": "known", "kind": "inproceedings", "missing_fields": ["booktitle"]}
    ]


def test_citation_audit_warns_on_unused_key_and_log_problem(tmp_path: Path) -> None:
    paper_dir = tmp_path / "paper"
    write_file(paper_dir / "main.tex", r"\citep{used}\bibliography{refs}")
    write_file(
        paper_dir / "refs.bib",
        r"""
@misc{used,
  author = {A. Author},
  title = {Used},
  year = {2026},
  url = {https://example.com/used}
}
@misc{unused,
  author = {B. Author},
  title = {Unused},
  year = {2026},
  url = {https://example.com/unused}
}
""",
    )
    write_file(paper_dir / "main.log", "LaTeX Warning: Citation `x' undefined on input line 1.\n")

    report = audit_paper_citations.audit_citations(
        paper_dir=paper_dir,
        bib_path=paper_dir / "refs.bib",
        log_path=paper_dir / "main.log",
    )

    assert report["status"] == "warning"
    assert report["unused_bib_keys"] == ["unused"]
    assert len(report["log_problems"]) == 1


def test_citation_audit_detects_duplicate_bib_keys(tmp_path: Path) -> None:
    paper_dir = tmp_path / "paper"
    write_file(paper_dir / "main.tex", r"\citep{dup}\bibliography{refs}")
    write_file(
        paper_dir / "refs.bib",
        r"""
@misc{dup,
  author = {A. Author},
  title = {First},
  year = {2026},
  url = {https://example.com/first}
}
@misc{dup,
  author = {B. Author},
  title = {Second},
  year = {2026},
  url = {https://example.com/second}
}
""",
    )
    write_file(paper_dir / "main.log", "Output written on main.pdf\n")

    report = audit_paper_citations.audit_citations(
        paper_dir=paper_dir,
        bib_path=paper_dir / "refs.bib",
        log_path=paper_dir / "main.log",
    )

    assert report["status"] == "blocker"
    assert report["duplicate_bib_keys"] == ["dup"]
