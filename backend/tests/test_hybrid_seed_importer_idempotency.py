import os
import unittest

os.environ.setdefault("DATABASE_URL", "postgresql://postgres:postgres@localhost/personaapp")
os.environ.setdefault("SECRET_KEY", "test-secret")

from app.db.hybrid_seed_importer import import_hybrid_seed_pack


class HybridSeedImporterIdempotencyTests(unittest.TestCase):
    def test_dry_run_import_is_repeatable(self):
        first_summary = import_hybrid_seed_pack(dry_run=True)
        second_summary = import_hybrid_seed_pack(dry_run=True)

        self.assertEqual(first_summary, second_summary)

        expected_tables = {
            "app_versions",
            "genes",
            "scenarios",
            "scenario_options",
            "option_weights",
            "sahaba_models",
            "advice_items",
            "advice_triggers",
        }
        self.assertEqual(set(first_summary.keys()), expected_tables)
        for table_name in expected_tables:
            self.assertGreater(first_summary[table_name], 0, msg=f"{table_name} should not be empty")


if __name__ == "__main__":
    unittest.main()
