"""AI-powered comment moderation."""

from typing import Any

from core.services.laya.base import LayaService


class CommentModerationService(LayaService):
    """Analyze weblog comments for moderation."""

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
        """Moderate a comment."""
        result = self.predict(body)

        answers = result["answers"]

        flags = {name: self._get_bool(answers.get(name)) for name in self.schema}

        return {
            "publishable": self._is_publishable(flags),
            "flags": flags,
            "raw": result,
        }

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
