from revtrack.openreview_tasks import build_issue_candidates, overlap_score


def test_overlap_score_prefers_shared_content_words() -> None:
    high = overlap_score(
        "The paper lacks latency experiments and memory ablations.",
        "We added latency experiments and memory ablations in Table 4.",
    )
    low = overlap_score(
        "The paper lacks latency experiments and memory ablations.",
        "Thank you for the detailed review and positive comments.",
    )
    assert high > low


def test_build_issue_candidates_extracts_review_and_response() -> None:
    submission = {
        "id": "sub1",
        "forum": "sub1",
        "version": 2,
        "content": {
            "title": "Demo Paper",
            "abstract": "Demo abstract.",
            "venueid": "ICLR.cc/2024/Conference",
        },
        "replies": [
            {
                "id": "rev1",
                "type": "official_review",
                "content": {
                    "weaknesses": "The paper lacks a strong baseline.",
                    "questions": "Could the authors add a stronger baseline comparison?",
                    "rating": "6: marginally above the acceptance threshold",
                    "confidence": "4: confident",
                },
            },
            {
                "id": "resp1",
                "type": "author_response",
                "signatures": ["ICLR.cc/2024/Conference/Submission1/Authors"],
                "content": {
                    "comment": "We added a stronger baseline in the revised version and report it in Table 3."
                },
            },
        ],
    }
    candidates = build_issue_candidates(submission)
    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate["issue_id"] == "sub1__r01"
    assert "baseline" in candidate["review_excerpt"].lower()
    assert "table 3" in candidate["aligned_response_excerpt"].lower()
    assert "revised version" in candidate["revision_summary"].lower()


def test_build_issue_candidates_repairs_neurips_rebuttal_type_from_invitations() -> None:
    submission = {
        "id": "sub1",
        "forum": "sub1",
        "version": 2,
        "content": {
            "title": "Demo Paper",
            "abstract": "Demo abstract.",
            "venueid": "NeurIPS.cc/2024/Conference",
        },
        "replies": [
            {
                "id": "rev1",
                "type": "official_review",
                "invitations": ["NeurIPS.cc/2024/Conference/Submission1/-/Official_Review"],
                "signatures": ["NeurIPS.cc/2024/Conference/Submission1/Reviewer_ABC"],
                "content": {
                    "weaknesses": "The paper lacks a strong baseline.",
                    "questions": "Could the authors add a stronger baseline comparison?",
                },
            },
            {
                "id": "rebuttal1",
                "type": "official_review",
                "invitations": [
                    "NeurIPS.cc/2024/Conference/Submission1/Official_Review1/-/Rebuttal"
                ],
                "signatures": ["NeurIPS.cc/2024/Conference/Submission1/Authors"],
                "content": {
                    "rebuttal": "We added a stronger baseline in Table 3 of the revised manuscript."
                },
            },
        ],
    }

    candidates = build_issue_candidates(submission)

    assert len(candidates) == 1
    assert candidates[0]["review_id"] == "rev1"
    assert "table 3" in candidates[0]["aligned_response_excerpt"].lower()
    assert "revised manuscript" in candidates[0]["revision_summary"].lower()
