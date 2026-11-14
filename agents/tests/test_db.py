import os, tempfile, unittest
os.environ["ABSURD_STATE_DIR"] = tempfile.mkdtemp()
from absurd_ops import db

class TestDB(unittest.TestCase):
    def setUp(self):
        db.init()

    def test_schema_and_runs(self):
        rid = db.log_run("test_agent", "checking")
        db.finish_run(rid, "ok", "done")
        row = db.one("SELECT * FROM agent_runs WHERE id=?", (rid,))
        self.assertEqual(row["status"], "ok")

    def test_task_queue_lifecycle(self):
        tid = db.enqueue("publish", {"slug": "x"})
        task = db.dequeue("publish")
        self.assertEqual(task["id"], tid)
        db.task_done(tid)
        self.assertIsNone(db.dequeue("publish"))

    def test_task_retry_then_dead(self):
        tid = db.enqueue("publish", {"slug": "y"})
        for _ in range(3):
            db.task_error(tid, "boom")
            db.dequeue("publish")
        row = db.one("SELECT status, attempts FROM tasks WHERE id=?", (tid,))
        self.assertEqual(row["status"], "dead")
        self.assertEqual(row["attempts"], 3)

if __name__ == "__main__":
    unittest.main()
