"""Check the draft's JSON and illustrate timing semantics, not schema conformance.

Run: python3 docs/research/agriculture-applicability/check_examples.py
No dependencies, network calls, or file writes.
"""

import json
import re
from pathlib import Path


def timing_match(window, event, days):
    """Illustrative three-valued evaluation: True, False, or None (unknown)."""
    lower = window.get("fromDays")
    upper = window.get("toDays")
    if lower is None and upper is None:
        raise ValueError("At least one day bound is needed")
    for bound in (lower, upper):
        if bound is not None and (type(bound) is not int or bound < 0):
            raise ValueError("Draft bounds are non-negative integers")
    if lower is not None and upper is not None and lower > upper:
        raise ValueError("Reversed bounds")
    if event != window["event"] or days is None:
        return None
    return (lower is None or days >= lower) and (upper is None or days <= upper)


def main():
    document = Path(__file__).with_name("README.md").read_text()
    blocks = re.findall(r"```json\n(.*?)\n```", document, re.DOTALL)
    assert blocks, "Missing draft JSON example"
    examples = [json.loads(block) for block in blocks]
    window = examples[0]["applicability"][0]["relativeTiming"]
    count = 0
    for event, days, expected in [
        ("Sowing", 19, False),
        ("Sowing", 20, True),
        ("Sowing", 25, True),
        ("Sowing", 30, True),
        ("Sowing", 31, False),
        ("Transplanting", 25, None),
        ("Sowing", None, None),
    ]:
        assert timing_match(window, event, days) is expected
        count += 1
    for invalid in [
        {"event": "Sowing"},
        {"event": "Sowing", "fromDays": 30, "toDays": 20},
        {"event": "Sowing", "fromDays": True},
        {"event": "Sowing", "fromDays": -1},
        {"event": "Sowing", "fromDays": 2.5},
    ]:
        try:
            timing_match(invalid, "Sowing", 25)
        except ValueError:
            count += 1
        else:
            raise AssertionError(f"Accepted invalid window: {invalid}")
    assert timing_match({"event": "Transplanting", "toDays": 10}, "Transplanting", 7)
    assert timing_match({"event": "Sowing", "fromDays": 20}, "Sowing", 50)
    count += 2
    print(f"Parsed {len(examples)} JSON block(s); passed {count} illustrative timing checks.")
    print("Not a production matcher, schema validator, or agronomic validation.")


if __name__ == "__main__":
    main()
