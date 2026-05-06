from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from revtrack.io import save_examples
from revtrack.schema import IssueExample


def build_examples() -> list[IssueExample]:
    return [
        IssueExample(
            id="smoke-001",
            source="synthetic_smoke",
            venue="demo",
            paper_title="Sparse Evidence Routing for Long-Context QA",
            abstract="A method for routing evidence chunks with sparse attention.",
            review_text="The paper claims efficiency gains but does not report latency or memory ablations.",
            author_response="We added a new latency and memory ablation in Table 4 and discuss deployment trade-offs in Section 5.",
            revision_summary="Revision adds Table 4 with latency and GPU memory under four context lengths, plus a new Section 5 discussion.",
            gold_label="fixed",
        ),
        IssueExample(
            id="smoke-002",
            source="synthetic_smoke",
            venue="demo",
            paper_title="Cross-Domain Retrieval Tuning",
            abstract="A retrieval tuning approach across domains.",
            review_text="Dataset licensing and consent are unclear for the newly collected corpus.",
            author_response="We appreciate the concern and will expand the ethical discussion in future work.",
            revision_summary="The revision does not add data licensing details or a collection protocol.",
            gold_label="unresolved",
        ),
        IssueExample(
            id="smoke-003",
            source="synthetic_smoke",
            venue="demo",
            paper_title="Chain-of-Plan Decoding",
            abstract="A decoding strategy for planning before generation.",
            review_text="The error analysis is too shallow and does not explain where the model still fails.",
            author_response="We added a short qualitative analysis of three failures and clarified typical planning errors.",
            revision_summary="A short paragraph with three examples was added, but no systematic error taxonomy appears.",
            gold_label="partially_fixed",
        ),
        IssueExample(
            id="smoke-004",
            source="synthetic_smoke",
            venue="demo",
            paper_title="Low-Resource Multilingual Alignment",
            abstract="A multilingual alignment method across 30 languages.",
            review_text="The paper lacks low-resource language analysis and may hide uneven performance.",
            author_response="We added low-resource results and re-ran the main table with a stronger prompt.",
            revision_summary="The revision adds eight low-resource languages, but removes one previous language and shows a notable average drop on the new setup.",
            gold_label="regressed",
        ),
        IssueExample(
            id="smoke-005",
            source="synthetic_smoke",
            venue="demo",
            paper_title="Calibration-Aware Reasoning",
            abstract="A reasoning method trained with calibration signals.",
            review_text="The confidence claims are unsupported because no calibration metric is reported.",
            author_response="We now report ECE and Brier score and add a reliability diagram in the appendix.",
            revision_summary="A new calibration section reports ECE, Brier score, and a reliability diagram.",
            gold_label="fixed",
        ),
        IssueExample(
            id="smoke-006",
            source="synthetic_smoke",
            venue="demo",
            paper_title="Adaptive Context Pruning",
            abstract="A context pruning strategy for tool-augmented agents.",
            review_text="The main baseline is missing, so it is hard to tell whether the gains are meaningful.",
            author_response="We agree this comparison is useful, but the experiment is beyond the current scope.",
            revision_summary="The missing baseline is still absent in the revised manuscript.",
            gold_label="unresolved",
        ),
        IssueExample(
            id="smoke-007",
            source="synthetic_smoke",
            venue="demo",
            paper_title="Provable Prompt Compression",
            abstract="A prompt compression method with approximation guarantees.",
            review_text="The theoretical guarantee seems overstated because the assumptions are not explicit.",
            author_response="We softened the claim, listed the assumptions clearly, and clarified when the guarantee applies.",
            revision_summary="The theorem statement is narrowed and assumptions are now explicit, but no new proof detail is added.",
            gold_label="partially_fixed",
        ),
        IssueExample(
            id="smoke-008",
            source="synthetic_smoke",
            venue="demo",
            paper_title="Self-Debugging Tool Agents",
            abstract="Agents that debug their own tool traces.",
            review_text="The method is reproducible in principle, but the exact prompt templates and seeds are missing.",
            author_response="We simplified the prompting pipeline and updated the reproducibility statement.",
            revision_summary="The revised paper uses a new prompt template, reports longer runtime, and still does not release exact seeds.",
            gold_label="regressed",
        ),
    ]


def main() -> None:
    output_path = ROOT / "data" / "samples" / "smoke.jsonl"
    save_examples(output_path, build_examples())
    print(f"Wrote smoke data to {output_path}")


if __name__ == "__main__":
    main()
