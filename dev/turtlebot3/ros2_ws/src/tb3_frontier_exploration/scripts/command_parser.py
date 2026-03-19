#!/usr/bin/env python3
"""
Minimal command parser for fake semantic navigation.
Input: raw text (e.g. "go to table").
Output: (success: bool, object_label: str | None, error_message: str | None).
No LLM, no speech; hardcoded keyword matching only.
"""

from __future__ import annotations

# Verbs we accept; the rest of the phrase is treated as the object name.
GO_VERBS = ("go to", "navigate to")

# Default allowed objects (can be overridden from semantic_goals.yaml at runtime).
DEFAULT_OBJECTS = frozenset({"table", "chair", "fridge"})


def parse_command(
    text: str,
    allowed_objects: set[str] | frozenset[str] | None = None,
) -> tuple[bool, str | None, str | None]:
    """
    Parse a raw command string and extract the target object label.

    Args:
        text: Raw input, e.g. "go to table".
        allowed_objects: Set of valid object labels (lowercase). If None, uses DEFAULT_OBJECTS.

    Returns:
        (success, object_label, error_message).
        - If valid: (True, "table", None).
        - If invalid: (False, None, "Unsupported command. Use: go to <object>.") or similar.
    """
    if allowed_objects is None:
        allowed_objects = DEFAULT_OBJECTS

    raw = (text or "").strip()
    if not raw:
        return False, None, "Empty command."

    lower = raw.lower()

    # Find which verb (if any) is present and get the remainder.
    remainder: str | None = None
    for verb in GO_VERBS:
        if lower.startswith(verb):
            remainder = raw[len(verb) :].strip().lower()
            break

    if remainder is None:
        return (
            False,
            None,
            "Unsupported command. Use: go to <object>.",
        )

    if not remainder:
        return False, None, "Missing object name. Use: go to <object>."

    # Take the first token as the object label (ignore extra words for now).
    object_label = remainder.split()[0] if remainder else ""

    if object_label not in allowed_objects:
        supported = ", ".join(sorted(allowed_objects))
        return (
            False,
            None,
            f"Unknown object '{object_label}'. Supported: {supported}.",
        )

    return True, object_label, None


# ---- Example usage and tests (run with: python3 command_parser.py) ----

def _run_tests() -> None:
    """Run a few example test cases."""
    cases = [
        ("go to table", True, "table"),
        ("  go to chair  ", True, "chair"),
        ("Go To Fridge", True, "fridge"),
        ("navigate to table", True, "table"),
        ("navigate to chair", True, "chair"),
        ("", False, None),
        ("pick up table", False, None),
        ("go to", False, None),
        ("go to sofa", False, None),
        ("go to TABLE", True, "table"),  # normalized to lowercase
    ]
    for raw, expect_ok, expect_obj in cases:
        ok, obj, err = parse_command(raw)
        assert ok == expect_ok and obj == expect_obj, (
            f"parse_command({raw!r}) -> ok={ok}, obj={obj}, err={err}"
        )
    print("All tests passed.")


if __name__ == "__main__":
    _run_tests()
