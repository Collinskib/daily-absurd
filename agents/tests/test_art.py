import tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from absurd_ops import art, config

class TestArt(unittest.TestCase):
    def test_art_deterministic(self):
        tmp = Path(tempfile.mkdtemp())
        with patch.object(config, "ART_DIR", tmp):
            a = art.ensure_art("slug-one", "sports", "A headline")
            b = art.ensure_art("slug-one", "sports", "A headline")
            self.assertEqual(a, b)
            self.assertTrue((tmp / a).exists())
            self.assertIn("<svg", (tmp / a).read_text())

if __name__ == "__main__":
    unittest.main()
