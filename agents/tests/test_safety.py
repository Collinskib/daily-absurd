import unittest
from absurd_ops.agents.safety_editor import _deterministic_check

def _draft(body="word " * 250, headline="X Does Y", source="A real thing happened"):
    return {"headline": headline, "subheadline": "s", "body": body, "sourceEvent": source}

class TestSafety(unittest.TestCase):
    def test_flags_emergency_language(self):
        d = _draft(body="word " * 200 + " BREAKING ALERT: evacuate now")
        self.assertTrue(_deterministic_check(d))

    def test_flags_missing_source(self):
        self.assertTrue(_deterministic_check(_draft(source="")))

    def test_clean_draft_passes(self):
        self.assertEqual(_deterministic_check(_draft()), [])

    def test_flags_sensitive(self):
        self.assertTrue(_deterministic_check(_draft(body="word " * 200 + " about a school shooting")))

if __name__ == "__main__":
    unittest.main()
