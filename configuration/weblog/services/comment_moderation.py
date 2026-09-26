"""AI-powered comment moderation."""

from typing import Any

import httpx

from core.services.laya.base import LayaService


class CommentModerationService(LayaService):
    """Analyze weblog comments for moderation."""

    #: Minimum calibrated confidence (0-1) Laya must have across *every*
    #: moderation flag before its publish/reject verdict is trusted and
    #: applied automatically. Below this, Laya isn't "sure enough" one
    #: way or the other (e.g. ~50/50), so the comment is routed to the
    #: article's author for manual verification instead.
    CONFIDENCE_THRESHOLD: float = 0.8

    schema: dict[str, Any] = {
        "is_spam": {
            "type": "noul",
            "instructions": (
                "Is this comment spam, including repetitive, automated, "
                "meaningless, or unsolicited promotional content?"
            ),
        },
        "contains_profanity": {
            "type": "noul",
            "instructions": (
                "Does the comment contain profanity, vulgar language, "
                "or explicit swear words?"
            ),
        },
        "contains_harassment": {
            "type": "noul",
            "instructions": (
                "Does the comment harass, insult, bully, or personally "
                "attack another person?"
            ),
        },
        "contains_hate_speech": {
            "type": "noul",
            "instructions": (
                "Does the comment contain hateful or degrading content "
                "targeting a person or protected group?"
            ),
        },
        "contains_threat": {
            "type": "noul",
            "instructions": (
                "Does the comment contain a threat of violence, harm, "
                "or intimidation?"
            ),
        },
        "contains_sexual_content": {
            "type": "noul",
            "instructions": (
                "Does the comment contain sexually explicit or graphic "
                "content inappropriate for an article comment section?"
            ),
        },
        "contains_malicious_content": {
            "type": "noul",
            "instructions": (
                "Does the comment contain malicious instructions, "
                "exploitation attempts, malware-related content, or "
                "instructions intended to compromise systems?"
            ),
        },
        "contains_personal_information": {
            "type": "noul",
            "instructions": (
                "Does the comment expose sensitive personal information "
                "such as passwords, credentials, private addresses, "
                "phone numbers, or financial information?"
            ),
        },
        "contains_promotion": {
            "type": "noul",
            "instructions": (
                "Is the primary purpose advertising, self-promotion, "
                "affiliate promotion, or promoting an unrelated product, "
                "service, website, or social account?"
            ),
        },
        "contains_suspicious_link": {
            "type": "noul",
            "instructions": (
                "Does the comment contain a suspicious, deceptive, "
                "or potentially malicious external link?"
            ),
        },
        "is_irrelevant": {
            "type": "noul",
            "instructions": ("Is the comment unrelated to the article or discussion?"),
        },
        "is_constructive": {
            "type": "noul",
            "instructions": (
                "Does the comment meaningfully contribute to the discussion?"
            ),
        },
    }

    def moderate(self, body: str) -> dict[str, Any]:
        """
        Moderate a comment.

        Returns:
            Structured moderation result with a publish/reject verdict
            plus how confident Laya is in that verdict overall. If the
            Laya server can't be reached, the verdict is marked as not
            confident (``confidence`` of ``0.0``) rather than raising,
            so callers fail safe into a human review instead of an
            error page.
        """
        try:
            result = self.predict(body)
        except httpx.RequestException:
            return {
                "publishable": False,
                "confidence": 0.0,
                "confident": False,
                "flags": {},
                "raw": None,
            }

        answers = result["answers"]

        flags = {name: self._get_bool(answers.get(name)) for name in self.schema}

        confidence = min(
            (self._get_confidence(answers.get(name)) for name in self.schema),
            default=0.0,
        )

        return {
            "publishable": self._is_publishable(flags),
            "confidence": confidence,
            "confident": confidence >= self.CONFIDENCE_THRESHOLD,
            "flags": flags,
            "raw": result,
        }

    def decide(self, body: str) -> tuple[str, dict[str, Any]]:
        """
        Decide what should happen to a newly submitted comment.

        Returns a ``(decision, moderation)`` tuple where ``decision`` is
        one of ``"approve"``, ``"reject"``, or ``"review"``. ``"review"``
        means Laya isn't confident enough (e.g. ~50/50, or Laya was
        unreachable) to auto-publish or auto-reject, so a human — the
        article's author — must verify the comment before it goes live.
        """
        moderation = self.moderate(body)

        if not moderation["confident"]:
            return "review", moderation

        decision = "approve" if moderation["publishable"] else "reject"

        return decision, moderation

    def decide_edit(self, body: str) -> tuple[str, dict[str, Any]]:
        """
        Decide what should happen to an edited comment.

        Unlike new comments, edits are never routed to the author for
        manual review: Laya's best-guess verdict (publish or reject) is
        applied directly even when Laya isn't fully confident in it (or
        was unreachable, in which case the edit is rejected out of an
        abundance of caution).
        """
        moderation = self.moderate(body)

        decision = "approve" if moderation["publishable"] else "reject"

        return decision, moderation

    @staticmethod
    def _get_confidence(answer: Any) -> float:
        """Extract Laya's calibrated confidence (0-1) for one flag."""
        if isinstance(answer, dict):
            value = answer.get(
                "answer_confidence",
                answer.get("confidence"),
            )

            if isinstance(value, (int, float)):
                return float(value)

        # An answer we don't recognize is treated as "no confidence" so
        # it forces a human review rather than being silently trusted.
        return 0.0

    @staticmethod
    def _get_bool(answer: Any) -> bool:
        """Normalize Laya boolean-like output."""
        if isinstance(answer, bool):
            return answer

        if isinstance(answer, dict):
            value = answer.get("noul")

            if isinstance(value, bool):
                return value

            if isinstance(value, str):
                return value.lower() in {
                    "true",
                    "yes",
                    "1",
                }

        if isinstance(answer, str):
            return answer.lower() in {
                "true",
                "yes",
                "1",
            }

        return False

    @staticmethod
    def _is_publishable(flags: dict[str, bool]) -> bool:
        """Determine whether a comment can be automatically published."""
        blocking_flags = {
            "is_spam",
            "contains_hate_speech",
            "contains_threat",
            "contains_sexual_content",
            "contains_malicious_content",
            "contains_personal_information",
            "contains_suspicious_link",
            "contains_harassment",
            "contains_profanity",
            "contains_promotion",
            "is_irrelevant",
        }

        return not any(flags.get(flag, False) for flag in blocking_flags)
