from dataclasses import dataclass
import unittest

from app.core.hybrid_engine import (
    GeneScoreResult,
    ModelMatchResult,
    _cosine_similarity,
    _select_activation_items,
    rank_gene_scores,
)


@dataclass
class DummyAdviceItem:
    advice_id: str
    channel: str
    advice_type: str
    title_en: str
    title_ar: str
    body_en: str
    body_ar: str
    priority: int


@dataclass
class DummyAdviceTrigger:
    trigger_id: str
    trigger_type: str
    gene_code: str
    model_code: str
    channel: str
    advice_id: str
    min_score: float
    max_score: float


class HybridEngineTests(unittest.TestCase):
    def test_rank_gene_scores_assigns_roles_and_normalizes(self):
        ranked = rank_gene_scores({"WIS": 6.0, "CRG": 4.0, "EMP": 2.0})

        self.assertEqual([entry.gene_code for entry in ranked[:3]], ["WIS", "CRG", "EMP"])
        self.assertEqual([entry.role for entry in ranked[:3]], ["dominant", "secondary", "support"])
        self.assertEqual([entry.normalized_score for entry in ranked[:3]], [100.0, 66.67, 33.33])

    def test_cosine_similarity_handles_zero_vector(self):
        self.assertEqual(_cosine_similarity([0.0, 0.0], [0.2, 0.4]), 0.0)

    def test_select_activation_items_falls_back_when_channel_has_no_hits(self):
        gene_scores = [
            GeneScoreResult(gene_code="WIS", raw_score=8.0, normalized_score=100.0, rank=1, role="dominant"),
            GeneScoreResult(gene_code="CRG", raw_score=6.0, normalized_score=75.0, rank=2, role="secondary"),
            GeneScoreResult(gene_code="EMP", raw_score=4.0, normalized_score=50.0, rank=3, role="support"),
        ]
        model_matches = [ModelMatchResult(model_code="ABUBAKR", similarity=0.95, rank=1)]

        advice_items = [
            DummyAdviceItem("A_WIS_B", "behavior", "activation", "B", "", "", "", 90),
            DummyAdviceItem("A_WIS_R", "reflection", "activation", "R", "", "", "", 90),
            DummyAdviceItem("A_SOC_LOW", "social", "activation", "S1", "", "", "", 80),
            DummyAdviceItem("A_SOC_HIGH", "social", "activation", "S2", "", "", "", 95),
        ]

        triggers = [
            DummyAdviceTrigger("T_B", "TOP_GENE", "WIS", None, "behavior", "A_WIS_B", 0, 100),
            DummyAdviceTrigger("T_R", "TOP_GENE", "WIS", None, "reflection", "A_WIS_R", 0, 100),
        ]

        selected = _select_activation_items(advice_items, triggers, gene_scores, model_matches)

        self.assertEqual([item.channel for item in selected], ["behavior", "reflection", "social"])
        self.assertEqual(selected[0].advice_id, "A_WIS_B")
        self.assertEqual(selected[1].advice_id, "A_WIS_R")
        self.assertEqual(selected[2].advice_id, "A_SOC_HIGH")
        self.assertTrue(selected[2].is_fallback)


if __name__ == "__main__":
    unittest.main()
