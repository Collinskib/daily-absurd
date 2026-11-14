import unittest
from absurd_ops.agents.opportunity_analyst import _heuristic_score, _guess_category

class TestAnalyst(unittest.TestCase):
    def test_absurd_story_scores_higher(self):
        s1, *_ = _heuristic_score("Thief returns stolen watch with apology note", "bizarre story", "AFP")
        s2, *_ = _heuristic_score("Committee meets to discuss framework", "routine", "Wire")
        self.assertGreater(s1, s2)

    def test_tragedy_flagged_risky(self):
        _, _, risky = _heuristic_score("Dozens killed in blast", "explosion", "Wire")
        self.assertTrue(risky)

    def test_category_guess(self):
        self.assertEqual(_guess_category("OpenAI releases new AI model"), "technology-ai")
        self.assertEqual(_guess_category("Election results announced"), "politics-government")
        self.assertEqual(_guess_category("Local bakery wins award"), "world-absurdities")

if __name__ == "__main__":
    unittest.main()
