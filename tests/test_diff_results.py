"""Tests for deterministic analysis snapshot diffs."""

import importlib.util
from pathlib import Path
import unittest


SCRIPT_PATH = (
    Path(__file__).parents[1]
    / "skills"
    / "morphiq-track"
    / "scripts"
    / "diff-results.py"
)
SPEC = importlib.util.spec_from_file_location("diff_results", SCRIPT_PATH)
diff_results = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(diff_results)


class DeterministicDiffTests(unittest.TestCase):
    def test_provider_and_competitor_keys_are_sorted(self):
        geo = diff_results.diff_geo(
            {"per_provider": {"zeta": 2, "alpha": 1}},
            {"per_provider": {"middle": 3}},
        )
        sov = diff_results.diff_sov(
            {"competitors": {"zeta": 2, "alpha": 1}},
            {"competitors": {"middle": 3}},
        )

        self.assertEqual(
            list(geo["per_provider"]), ["alpha", "middle", "zeta"]
        )
        self.assertEqual(
            list(sov["competitors"]), ["alpha", "middle", "zeta"]
        )

    def test_citation_groups_are_sorted_by_unique_key(self):
        current = [
            {"url": "https://z.example", "provider": "beta", "prompt": "two"},
            {"url": "https://y.example", "provider": "beta", "prompt": "stable"},
            {"url": "https://a.example", "provider": "alpha", "prompt": "one"},
            {"url": "https://b.example", "provider": "alpha", "prompt": "stable"},
        ]
        previous = [
            {"url": "https://x.example", "provider": "beta", "prompt": "old"},
            {"url": "https://y.example", "provider": "beta", "prompt": "stable"},
            {"url": "https://c.example", "provider": "alpha", "prompt": "old"},
            {"url": "https://b.example", "provider": "alpha", "prompt": "stable"},
        ]

        result = diff_results.diff_citations(current, previous)

        self.assertEqual(
            [citation["url"] for citation in result["gained"]],
            ["https://a.example", "https://z.example"],
        )
        self.assertEqual(
            [citation["url"] for citation in result["lost"]],
            ["https://c.example", "https://x.example"],
        )
        self.assertEqual(
            [citation["url"] for citation in result["stable"]],
            ["https://b.example", "https://y.example"],
        )


if __name__ == "__main__":
    unittest.main()
