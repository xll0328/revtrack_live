from __future__ import annotations

import requests

from revtrack.openreview_api import OpenReviewClient, detect_reply_type, normalize_submission


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.content = b""

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self.payload


class FakeSession:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    def mount(self, *_args: object, **_kwargs: object) -> None:
        return None

    def get(self, url: str, params: dict | None = None, timeout: int | None = None) -> FakeResponse:
        del timeout
        params = params or {}
        self.calls.append((url, params))
        if url.endswith("/notes/search"):
            return FakeResponse(
                {
                    "notes": [
                        {
                            "id": "forum1",
                            "forum": "forum1",
                            "content": {"venueid": {"value": "ICLR.cc/2025/Conference"}},
                        }
                    ]
                }
            )
        if params.get("forum") == "forum1":
            return FakeResponse(
                {
                    "notes": [
                        {"id": "forum1", "forum": "forum1"},
                        {
                            "id": "reply1",
                            "forum": "forum1",
                            "invitation": "ICLR.cc/2025/Conference/Submission1/-/Official_Review",
                            "content": {"weaknesses": {"value": "Need a stronger baseline."}},
                        },
                    ]
                }
            )
        return FakeResponse({"notes": []})


class ProxyFailingSession(FakeSession):
    def get(self, url: str, params: dict | None = None, timeout: int | None = None) -> FakeResponse:
        del url, params, timeout
        raise requests.exceptions.ProxyError("proxy blocked")


class DirectSuccessSession(FakeSession):
    def get(self, url: str, params: dict | None = None, timeout: int | None = None) -> FakeResponse:
        del url, timeout
        self.calls.append(("direct", params or {}))
        return FakeResponse(
            {
                "notes": [
                    {
                        "id": "forum_direct",
                        "forum": "forum_direct",
                        "content": {"venueid": {"value": "ICLR.cc/2025/Conference"}},
                    }
                ]
            }
        )


def test_detect_reply_type_accepts_v1_invitation_field() -> None:
    note = {"invitation": "ICLR.cc/2025/Conference/Submission1/-/Official_Review"}
    assert detect_reply_type(note) == "official_review"


def test_detect_reply_type_treats_author_rebuttal_as_response_before_official_review() -> None:
    note = {
        "invitations": [
            "NeurIPS.cc/2024/Conference/Submission21129/Official_Review1/-/Rebuttal",
            "NeurIPS.cc/2024/Conference/-/Edit",
        ],
        "signatures": ["NeurIPS.cc/2024/Conference/Submission21129/Authors"],
    }

    assert detect_reply_type(note) == "author_response"


def test_detect_reply_type_accepts_author_rebuttal_invitation() -> None:
    note = {
        "invitations": ["NeurIPS.cc/2024/Conference/Submission21129/-/Author_Rebuttal"],
        "signatures": ["NeurIPS.cc/2024/Conference/Submission21129/Authors"],
    }

    assert detect_reply_type(note) == "author_response"


def test_v2_search_hydrates_forum_replies() -> None:
    session = FakeSession()
    client = OpenReviewClient(session=session, api_mode="v2-search")

    notes = client.list_submissions("ICLR.cc/2025/Conference", limit=1)

    assert notes[0]["details"]["replies"][0]["id"] == "reply1"
    assert session.calls[0][0].endswith("/notes/search")
    assert session.calls[0][1]["venueid"] == "ICLR.cc/2025/Conference"
    assert session.calls[1][1]["forum"] == "forum1"


def test_auto_mode_falls_back_from_empty_v2_notes_to_search() -> None:
    session = FakeSession()
    client = OpenReviewClient(session=session, api_mode="auto")

    notes = client.iter_submissions("ICLR.cc/2025/Conference", limit=1)

    assert len(notes) == 1
    assert notes[0]["id"] == "forum1"
    assert session.calls[0][0].endswith("/notes")
    assert session.calls[1][0].endswith("/notes/search")


def test_default_api_mode_is_v2_notes() -> None:
    client = OpenReviewClient(session=FakeSession())
    assert client.api_mode == "v2-notes"


def test_proxy_failure_retries_with_direct_session() -> None:
    direct_session = DirectSuccessSession()
    client = OpenReviewClient(
        session=ProxyFailingSession(),
        direct_session=direct_session,
        api_mode="v2-notes",
    )

    notes = client.list_submissions("ICLR.cc/2025/Conference", limit=1)

    assert notes[0]["id"] == "forum_direct"
    assert direct_session.calls[0][0] == "direct"
    assert [event["event"] for event in client.diagnostics] == [
        "proxy_request_failed",
        "direct_retry_succeeded",
    ]


def test_normalize_submission_keeps_v1_reply_invitations() -> None:
    submission = {
        "id": "forum1",
        "forum": "forum1",
        "content": {"venueid": {"value": "ICLR.cc/2025/Conference"}},
        "details": {
            "replies": [
                {
                    "id": "reply1",
                    "forum": "forum1",
                    "invitation": "ICLR.cc/2025/Conference/Submission1/-/Official_Review",
                    "content": {"weaknesses": {"value": "Need a stronger baseline."}},
                }
            ]
        },
    }

    normalized = normalize_submission(submission)

    assert normalized["venueid"] == "ICLR.cc/2025/Conference"
    assert normalized["replies"][0]["type"] == "official_review"
    assert normalized["replies"][0]["invitations"] == [
        "ICLR.cc/2025/Conference/Submission1/-/Official_Review"
    ]
