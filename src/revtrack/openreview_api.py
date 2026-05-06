from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


API2_BASE = "https://api2.openreview.net"
API1_BASE = "https://api.openreview.net"
WEB_BASE = "https://openreview.net"
DEFAULT_API_MODE = "v2-notes"


class OpenReviewRequestError(RuntimeError):
    """Raised when the OpenReview API cannot be reached or returns an invalid response."""


def normalize_value(value: Any) -> Any:
    if isinstance(value, dict) and "value" in value:
        return value["value"]
    if isinstance(value, list):
        return [normalize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: normalize_value(item) for key, item in value.items()}
    return value


def invitation_suffix(invitation: str) -> str:
    return invitation.split("/")[-1]


def note_invitations(note: dict[str, Any]) -> list[str]:
    invitations = note.get("invitations", [])
    if isinstance(invitations, str):
        invitations = [invitations]
    else:
        invitations = list(invitations or [])
    invitation = note.get("invitation")
    if invitation:
        invitations.append(str(invitation))
    return invitations


def detect_reply_type(note: dict[str, Any]) -> str:
    invitations = note_invitations(note)
    joined = " ".join(invitations)
    signatures = " ".join(note.get("signatures", []))
    if "Author_Rebuttal" in joined:
        return "author_response"
    if "Rebuttal" in joined and "Authors" in signatures:
        return "author_response"
    if "Official_Review" in joined:
        return "official_review"
    if "Meta_Review" in joined:
        return "meta_review"
    if "Decision" in joined:
        return "decision"
    if "Official_Comment" in joined:
        if "Authors" in signatures:
            return "author_response"
        return "official_comment"
    if "Public_Comment" in joined:
        return "public_comment"
    return "other"


def summarize_long_text_fields(content: dict[str, Any], min_chars: int = 80) -> list[dict[str, str]]:
    fields: list[dict[str, str]] = []
    for key, value in content.items():
        if not isinstance(value, str):
            continue
        text = " ".join(value.split())
        if len(text) >= min_chars:
            fields.append({"field": key, "text": text})
    fields.sort(key=lambda item: len(item["text"]), reverse=True)
    return fields


@dataclass
class OpenReviewClient:
    session: requests.Session | None = None
    direct_session: requests.Session | None = None
    api_mode: str = DEFAULT_API_MODE
    api2_base: str = API2_BASE
    api1_base: str = API1_BASE
    web_base: str = WEB_BASE
    request_timeout: int = 30
    retry_total: int = 5
    retry_backoff: float = 1.0
    fallback_without_proxy: bool = True
    diagnostics: list[dict[str, Any]] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        valid_modes = {"auto", "v2-notes", "v2-search", "v1-notes"}
        if self.api_mode not in valid_modes:
            raise ValueError(f"Unsupported OpenReview API mode: {self.api_mode}")
        self.session = self.session or self._new_session(trust_env=True)
        self._configure_session(self.session)
        if self.direct_session is not None:
            self._configure_session(self.direct_session, trust_env=False)

    def _new_session(self, *, trust_env: bool) -> requests.Session:
        session = requests.Session()
        session.trust_env = trust_env
        self._configure_session(session)
        return session

    def _configure_session(self, session: requests.Session, trust_env: bool | None = None) -> None:
        if trust_env is not None:
            session.trust_env = trust_env
        retry = Retry(
            total=self.retry_total,
            connect=self.retry_total,
            read=self.retry_total,
            backoff_factor=self.retry_backoff,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

    def _get_direct_session(self) -> requests.Session:
        if self.direct_session is None:
            self.direct_session = self._new_session(trust_env=False)
        return self.direct_session

    @staticmethod
    def _looks_like_proxy_failure(exc: requests.RequestException) -> bool:
        text = str(exc).lower()
        return isinstance(exc, requests.exceptions.ProxyError) or "proxy" in text

    def _diagnostic_event(
        self,
        *,
        event: str,
        url: str,
        params: dict[str, Any],
        error: Exception | None = None,
        session_kind: str,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "event": event,
            "url": url,
            "params": params,
            "session": session_kind,
        }
        if error is not None:
            payload["error_type"] = type(error).__name__
            payload["error"] = str(error)
        self.diagnostics.append(payload)
        return payload

    def _request_json_once(
        self,
        session: requests.Session,
        url: str,
        params: dict[str, Any],
        timeout: int,
    ) -> dict[str, Any]:
        response = session.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise OpenReviewRequestError(
                f"OpenReview returned unexpected payload for {url}: {type(payload).__name__}"
            )
        return payload

    def _get_json(
        self,
        api_base: str,
        path: str,
        params: dict[str, Any],
        *,
        timeout: int | None = None,
    ) -> dict[str, Any]:
        assert self.session is not None
        url = f"{api_base}{path}"
        request_timeout = timeout or self.request_timeout
        try:
            payload = self._request_json_once(self.session, url, params, request_timeout)
        except requests.RequestException as exc:
            if self.fallback_without_proxy and self._looks_like_proxy_failure(exc):
                self._diagnostic_event(
                    event="proxy_request_failed",
                    url=url,
                    params=params,
                    error=exc,
                    session_kind="env",
                )
                direct_session = self._get_direct_session()
                try:
                    payload = self._request_json_once(direct_session, url, params, request_timeout)
                except requests.RequestException as direct_exc:
                    self._diagnostic_event(
                        event="direct_retry_failed",
                        url=url,
                        params=params,
                        error=direct_exc,
                        session_kind="direct",
                    )
                    raise OpenReviewRequestError(
                        f"OpenReview request failed for {url} with params {params}; "
                        f"env-proxy error: {exc}; direct retry error: {direct_exc}"
                    ) from direct_exc
                except ValueError as direct_exc:
                    raise OpenReviewRequestError(
                        f"OpenReview returned non-JSON response for {url} with params {params}"
                    ) from direct_exc
                self._diagnostic_event(
                    event="direct_retry_succeeded",
                    url=url,
                    params=params,
                    session_kind="direct",
                )
                return payload
            raise OpenReviewRequestError(
                f"OpenReview request failed for {url} with params {params}: {exc}"
            ) from exc
        except ValueError as exc:
            raise OpenReviewRequestError(
                f"OpenReview returned non-JSON response for {url} with params {params}"
            ) from exc
        return payload

    def list_submissions(
        self,
        venue_id: str,
        limit: int = 100,
        details: str = "replies",
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        if self.api_mode == "v2-notes":
            return self.list_submissions_v2_notes(venue_id, limit, details, offset)
        if self.api_mode == "v2-search":
            return self.list_submissions_v2_search(venue_id, limit, offset)
        if self.api_mode == "v1-notes":
            return self.list_submissions_v1_notes(venue_id, limit, details, offset)

        errors = []
        for mode, getter in [
            ("v2-notes", self.list_submissions_v2_notes),
            ("v2-search", self.list_submissions_v2_search),
            ("v1-notes", self.list_submissions_v1_notes),
        ]:
            try:
                if mode == "v2-search":
                    batch = getter(venue_id, limit, offset)
                else:
                    batch = getter(venue_id, limit, details, offset)
            except OpenReviewRequestError as exc:
                errors.append(str(exc))
                continue
            if batch or offset > 0:
                return batch
        if errors:
            raise OpenReviewRequestError("All OpenReview API modes failed:\n" + "\n".join(errors))
        return []

    def list_submissions_v2_notes(
        self,
        venue_id: str,
        limit: int = 100,
        details: str = "replies",
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        payload = self._get_json(
            self.api2_base,
            "/notes",
            params={
                "content.venueid": venue_id,
                "details": details,
                "limit": limit,
                "offset": offset,
            },
        )
        return payload.get("notes", [])

    def list_submissions_v2_search(
        self,
        venue_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        payload = self._get_json(
            self.api2_base,
            "/notes/search",
            params={
                "venueid": venue_id,
                "source": "forum",
                "limit": limit,
                "offset": offset,
            },
        )
        notes = payload.get("notes", [])
        for note in notes:
            note.setdefault("details", {})
            if "replies" not in note["details"]:
                note["details"]["replies"] = self.list_forum_replies(note.get("id", ""))
        return notes

    def list_submissions_v1_notes(
        self,
        venue_id: str,
        limit: int = 100,
        details: str = "replies",
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        payload = self._get_json(
            self.api1_base,
            "/notes",
            params={
                "content.venueid": venue_id,
                "details": details,
                "limit": limit,
                "offset": offset,
            },
        )
        return payload.get("notes", [])

    def list_forum_replies(self, forum_id: str, limit: int = 1000) -> list[dict[str, Any]]:
        if not forum_id:
            return []
        payload = self._get_json(
            self.api2_base,
            "/notes",
            params={
                "forum": forum_id,
                "limit": limit,
            },
        )
        return [
            note
            for note in payload.get("notes", [])
            if note.get("id") != forum_id
        ]

    def iter_submissions(self, venue_id: str, limit: int = 100) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        offset = 0
        page_size = min(limit, 100)
        while len(results) < limit:
            batch = self.list_submissions(
                venue_id=venue_id,
                limit=min(page_size, limit - len(results)),
                offset=offset,
            )
            if not batch:
                break
            results.extend(batch)
            offset += len(batch)
            if len(batch) < page_size:
                break
        return results

    def download_pdf(self, pdf_path: str, output_path: str | Path) -> Path:
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        assert self.session is not None
        try:
            response = self.session.get(f"{self.web_base}{pdf_path}", timeout=max(60, self.request_timeout))
            response.raise_for_status()
        except requests.RequestException as exc:
            raise OpenReviewRequestError(f"Could not download OpenReview PDF {pdf_path}: {exc}") from exc
        target.write_bytes(response.content)
        return target


def normalize_submission(note: dict[str, Any]) -> dict[str, Any]:
    content = normalize_value(note.get("content", {}))
    replies = []
    for reply in note.get("details", {}).get("replies", []):
        normalized_content = normalize_value(reply.get("content", {}))
        replies.append(
            {
                "id": reply.get("id"),
                "forum": reply.get("forum"),
                "replyto": reply.get("replyto"),
                "type": detect_reply_type(reply),
                "signatures": reply.get("signatures", []),
                "invitations": note_invitations(reply),
                "content": normalized_content,
                "long_text_fields": summarize_long_text_fields(normalized_content),
            }
        )

    return {
        "id": note.get("id"),
        "forum": note.get("forum"),
        "number": note.get("number"),
        "version": note.get("version", 1),
        "content": content,
        "venueid": content.get("venueid", ""),
        "pdf_path": content.get("pdf", ""),
        "replies": replies,
    }
