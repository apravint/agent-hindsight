import unittest
import tempfile
import os
from agent_hindsight.memory import HindsightStore

class TestHindsight(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_memory.db")
        self.store = HindsightStore(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_retain_and_recall(self):
        res = self.store.retain("Postgres runs on port 5432 with replication enabled", category="database", importance=8)
        self.assertTrue(res["ok"])
        self.assertEqual(res["id"], 1)

        # Recall with keyword
        matches = self.store.recall("postgres replication")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["category"], "database")
        self.assertIn("Postgres runs on port 5432", matches[0]["fact"])

    def test_reflection(self):
        self.store.retain("API uses JWT tokens", category="security", importance=9)
        self.store.retain("Database is on 5432", category="database", importance=7)
        
        reflection = self.store.reflect()
        self.assertEqual(reflection["total_memories"], 2)
        self.assertEqual(reflection["categories_count"], 2)

if __name__ == "__main__":
    unittest.main()
