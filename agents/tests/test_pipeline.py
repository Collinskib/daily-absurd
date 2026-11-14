import os, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
os.environ["ABSURD_STATE_DIR"] = tempfile.mkdtemp()
from absurd_ops import db, config
from absurd_ops.pipeline import sync_subscribers

class TestPipeline(unittest.TestCase):
    def test_sync_subscribers(self):
        db.init()
        tmp = Path(tempfile.mkdtemp())
        (tmp / "content").mkdir()
        f = tmp / "content" / "subscribers.ndjson"
        f.write_text(
            '{"email":"a@x.com","status":"subscribed"}\n'
            '{"email":"b@x.com","status":"unsubscribed"}\n'
            '{"email":"a@x.com","status":"unsubscribed"}\n'
        )
        with patch.object(config, "WEB_DIR", tmp):
            n = sync_subscribers()
        self.assertEqual(n, 3)
        rows = {r["email"]: r["status"] for r in db.query("SELECT * FROM subscribers")}
        self.assertEqual(rows, {"a@x.com": "unsubscribed", "b@x.com": "unsubscribed"})

if __name__ == "__main__":
    unittest.main()
