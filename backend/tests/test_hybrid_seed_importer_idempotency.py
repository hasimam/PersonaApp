import os
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker

os.environ.setdefault("DATABASE_URL", "postgresql://postgres:postgres@localhost/personaapp")
os.environ.setdefault("SECRET_KEY", "test-secret")

from app.db.hybrid_seed_importer import _default_seed_dir, _import_hybrid_seed_pack
from app.db.session import Base
from app.models import (
    AdviceItem,
    AdviceTrigger,
    AppVersion,
    Gene,
    OptionWeight,
    ProphetTrait,
    ProphetTraitGeneWeight,
    QuranValue,
    QuranValueGeneWeight,
    SahabaModel,
    Scenario,
    ScenarioOption,
)


@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(_type, _compiler, **_kwargs):
    return "TEXT"


class HybridSeedImporterIdempotencyTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(
            bind=self.engine,
            tables=[
                AppVersion.__table__,
                Gene.__table__,
                Scenario.__table__,
                ScenarioOption.__table__,
                OptionWeight.__table__,
                SahabaModel.__table__,
                AdviceItem.__table__,
                AdviceTrigger.__table__,
                QuranValue.__table__,
                ProphetTrait.__table__,
                QuranValueGeneWeight.__table__,
                ProphetTraitGeneWeight.__table__,
            ],
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = self.SessionLocal()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(
            bind=self.engine,
            tables=[
                ProphetTraitGeneWeight.__table__,
                QuranValueGeneWeight.__table__,
                ProphetTrait.__table__,
                QuranValue.__table__,
                AdviceTrigger.__table__,
                AdviceItem.__table__,
                SahabaModel.__table__,
                OptionWeight.__table__,
                ScenarioOption.__table__,
                Scenario.__table__,
                Gene.__table__,
                AppVersion.__table__,
            ],
        )
        self.engine.dispose()

    def _table_counts(self):
        return {
            "app_versions": self.db.query(AppVersion).count(),
            "genes": self.db.query(Gene).count(),
            "scenarios": self.db.query(Scenario).count(),
            "scenario_options": self.db.query(ScenarioOption).count(),
            "option_weights": self.db.query(OptionWeight).count(),
            "sahaba_models": self.db.query(SahabaModel).count(),
            "advice_items": self.db.query(AdviceItem).count(),
            "advice_triggers": self.db.query(AdviceTrigger).count(),
            "quran_values": self.db.query(QuranValue).count(),
            "prophet_traits": self.db.query(ProphetTrait).count(),
            "quran_value_gene_weights": self.db.query(QuranValueGeneWeight).count(),
            "prophet_trait_gene_weights": self.db.query(ProphetTraitGeneWeight).count(),
        }

    def test_import_upsert_is_idempotent_in_database_state(self):
        with patch("app.db.hybrid_seed_importer.pg_insert", sqlite_insert):
            first_summary = _import_hybrid_seed_pack(db=self.db, seed_path=_default_seed_dir())
            self.db.commit()
            first_counts = self._table_counts()

            second_summary = _import_hybrid_seed_pack(db=self.db, seed_path=_default_seed_dir())
            self.db.commit()
            second_counts = self._table_counts()

        self.assertEqual(first_summary, second_summary)
        self.assertEqual(first_counts, second_counts)
        for table_name, count in first_counts.items():
            self.assertGreater(count, 0, msg=f"{table_name} should not be empty")


if __name__ == "__main__":
    unittest.main()
