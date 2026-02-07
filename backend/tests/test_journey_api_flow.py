import os
import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker

os.environ.setdefault("DATABASE_URL", "postgresql://postgres:postgres@localhost/personaapp")
os.environ.setdefault("SECRET_KEY", "test-secret")

from app.api.journey import cancel_journey, start_journey, submit_journey_answers, submit_journey_feedback
from app.db.session import Base
from app.models import (
    AdviceItem,
    AdviceTrigger,
    Answer,
    AppVersion,
    ComputedGeneScore,
    ComputedModelMatch,
    Feedback,
    Gene,
    OptionWeight,
    ProphetTrait,
    ProphetTraitGeneWeight,
    QuranValue,
    QuranValueGeneWeight,
    SahabaModel,
    Scenario,
    ScenarioOption,
    TestRun,
)
from app.schemas.journey import (
    JourneyAnswerSubmission,
    JourneyCancelRequest,
    JourneyFeedbackRequest,
    JourneyStartRequest,
    JourneySubmitAnswersRequest,
)


@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(_type, _compiler, **_kwargs):
    return "TEXT"


class JourneyApiFlowTests(unittest.TestCase):
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
                TestRun.__table__,
                Answer.__table__,
                ComputedGeneScore.__table__,
                ComputedModelMatch.__table__,
                Feedback.__table__,
            ],
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = self.SessionLocal()
        self._seed_minimal_journey_data()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(
            bind=self.engine,
            tables=[
                ProphetTraitGeneWeight.__table__,
                QuranValueGeneWeight.__table__,
                ProphetTrait.__table__,
                QuranValue.__table__,
                Feedback.__table__,
                ComputedModelMatch.__table__,
                ComputedGeneScore.__table__,
                Answer.__table__,
                TestRun.__table__,
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

    def _seed_minimal_journey_data(self):
        self.db.add(
            AppVersion(
                version_id="v_test",
                name="Test Version",
                is_active=True,
            )
        )

        self.db.add_all(
            [
                Gene(
                    version_id="v_test",
                    gene_code="WIS",
                    name_en="Wisdom",
                    name_ar="حكمة",
                    desc_en="Wisdom gene",
                    desc_ar="جين الحكمة",
                ),
                Gene(
                    version_id="v_test",
                    gene_code="CRG",
                    name_en="Courage",
                    name_ar="شجاعة",
                    desc_en="Courage gene",
                    desc_ar="جين الشجاعة",
                ),
                Gene(
                    version_id="v_test",
                    gene_code="EMP",
                    name_en="Empathy",
                    name_ar="تعاطف",
                    desc_en="Empathy gene",
                    desc_ar="جين التعاطف",
                ),
            ]
        )

        self.db.add_all(
            [
                Scenario(
                    version_id="v_test",
                    scenario_code="S01",
                    scenario_set_code="base",
                    order_index=1,
                    scenario_text_en="Scenario 1",
                    scenario_text_ar="الموقف 1",
                ),
                Scenario(
                    version_id="v_test",
                    scenario_code="S02",
                    scenario_set_code="base",
                    order_index=2,
                    scenario_text_en="Scenario 2",
                    scenario_text_ar="الموقف 2",
                ),
                Scenario(
                    version_id="v_test",
                    scenario_code="B01",
                    scenario_set_code="set_b",
                    order_index=1,
                    scenario_text_en="Scenario B1",
                    scenario_text_ar="الموقف ب1",
                ),
                Scenario(
                    version_id="v_test",
                    scenario_code="B02",
                    scenario_set_code="set_b",
                    order_index=2,
                    scenario_text_en="Scenario B2",
                    scenario_text_ar="الموقف ب2",
                ),
            ]
        )

        self.db.add_all(
            [
                ScenarioOption(
                    version_id="v_test",
                    scenario_code="S01",
                    option_code="A",
                    option_text_en="S01 A",
                    option_text_ar="الخيار أ",
                ),
                ScenarioOption(
                    version_id="v_test",
                    scenario_code="S01",
                    option_code="B",
                    option_text_en="S01 B",
                    option_text_ar="الخيار ب",
                ),
                ScenarioOption(
                    version_id="v_test",
                    scenario_code="S02",
                    option_code="A",
                    option_text_en="S02 A",
                    option_text_ar="الخيار أ",
                ),
                ScenarioOption(
                    version_id="v_test",
                    scenario_code="S02",
                    option_code="B",
                    option_text_en="S02 B",
                    option_text_ar="الخيار ب",
                ),
                ScenarioOption(
                    version_id="v_test",
                    scenario_code="B01",
                    option_code="A",
                    option_text_en="B01 A",
                    option_text_ar="الخيار أ",
                ),
                ScenarioOption(
                    version_id="v_test",
                    scenario_code="B01",
                    option_code="B",
                    option_text_en="B01 B",
                    option_text_ar="الخيار ب",
                ),
                ScenarioOption(
                    version_id="v_test",
                    scenario_code="B02",
                    option_code="A",
                    option_text_en="B02 A",
                    option_text_ar="الخيار أ",
                ),
                ScenarioOption(
                    version_id="v_test",
                    scenario_code="B02",
                    option_code="B",
                    option_text_en="B02 B",
                    option_text_ar="الخيار ب",
                ),
            ]
        )

        self.db.add_all(
            [
                OptionWeight(
                    version_id="v_test",
                    scenario_code="S01",
                    option_code="A",
                    gene_code="WIS",
                    weight=5.0,
                ),
                OptionWeight(
                    version_id="v_test",
                    scenario_code="S01",
                    option_code="B",
                    gene_code="CRG",
                    weight=5.0,
                ),
                OptionWeight(
                    version_id="v_test",
                    scenario_code="S02",
                    option_code="A",
                    gene_code="CRG",
                    weight=3.0,
                ),
                OptionWeight(
                    version_id="v_test",
                    scenario_code="S02",
                    option_code="B",
                    gene_code="EMP",
                    weight=4.0,
                ),
                OptionWeight(
                    version_id="v_test",
                    scenario_code="B01",
                    option_code="A",
                    gene_code="EMP",
                    weight=5.0,
                ),
                OptionWeight(
                    version_id="v_test",
                    scenario_code="B01",
                    option_code="B",
                    gene_code="CRG",
                    weight=5.0,
                ),
                OptionWeight(
                    version_id="v_test",
                    scenario_code="B02",
                    option_code="A",
                    gene_code="WIS",
                    weight=3.0,
                ),
                OptionWeight(
                    version_id="v_test",
                    scenario_code="B02",
                    option_code="B",
                    gene_code="EMP",
                    weight=4.0,
                ),
            ]
        )

        self.db.add(
            SahabaModel(
                version_id="v_test",
                model_code="MODEL_1",
                name_en="Model 1",
                name_ar="النموذج 1",
                summary_ar="ملخص",
                gene_vector_jsonb={"WIS": 1.0, "CRG": 0.8, "EMP": 0.6},
            )
        )

        self.db.add_all(
            [
                AdviceItem(
                    version_id="v_test",
                    advice_id="ACT_BEH",
                    channel="behavior",
                    advice_type="activation",
                    title_en="Behavior action",
                    title_ar="سلوك",
                    body_en="Do one behavior action",
                    body_ar="قم بسلوك واحد",
                    priority=100,
                ),
                AdviceItem(
                    version_id="v_test",
                    advice_id="ACT_REF",
                    channel="reflection",
                    advice_type="activation",
                    title_en="Reflection action",
                    title_ar="تأمل",
                    body_en="Do one reflection action",
                    body_ar="قم بتأمل واحد",
                    priority=100,
                ),
                AdviceItem(
                    version_id="v_test",
                    advice_id="ACT_SOC",
                    channel="social",
                    advice_type="activation",
                    title_en="Social action",
                    title_ar="اجتماعي",
                    body_en="Do one social action",
                    body_ar="قم بفعل اجتماعي",
                    priority=100,
                ),
                AdviceItem(
                    version_id="v_test",
                    advice_id="ACT_OTHER",
                    channel="behavior",
                    advice_type="activation",
                    title_en="Other behavior action",
                    title_ar="سلوك آخر",
                    body_en="This action is not part of the triggered three",
                    body_ar="هذا الإجراء ليس ضمن الخيارات الثلاثة",
                    priority=100,
                ),
            ]
        )

        self.db.add_all(
            [
                AdviceTrigger(
                    version_id="v_test",
                    trigger_id="TR_BEH",
                    trigger_type="TOP_GENE",
                    gene_code="WIS",
                    model_code=None,
                    channel="behavior",
                    advice_id="ACT_BEH",
                    min_score=0.0,
                    max_score=100.0,
                ),
                AdviceTrigger(
                    version_id="v_test",
                    trigger_id="TR_REF",
                    trigger_type="ANY",
                    gene_code=None,
                    model_code=None,
                    channel="reflection",
                    advice_id="ACT_REF",
                    min_score=0.0,
                    max_score=100.0,
                ),
                AdviceTrigger(
                    version_id="v_test",
                    trigger_id="TR_SOC",
                    trigger_type="ANY",
                    gene_code=None,
                    model_code=None,
                    channel="social",
                    advice_id="ACT_SOC",
                    min_score=0.0,
                    max_score=100.0,
                ),
            ]
        )

        self.db.commit()

    def test_full_journey_api_flow(self):
        started = start_journey(payload=JourneyStartRequest(version_id="v_test"), db=self.db)
        self.assertEqual(started.version_id, "v_test")
        self.assertEqual(len(started.scenarios), 2)
        scenario_codes = [item.scenario_code for item in started.scenarios]
        self.assertIn(scenario_codes, [["S01", "S02"], ["B01", "B02"]])
        self.assertEqual(self.db.query(TestRun).filter(TestRun.id == started.test_run_id).first().status, "started")

        submitted = submit_journey_answers(
            payload=JourneySubmitAnswersRequest(
                version_id="v_test",
                test_run_id=started.test_run_id,
                answers=[
                    JourneyAnswerSubmission(scenario_code=scenario_codes[0], option_code="A"),
                    JourneyAnswerSubmission(scenario_code=scenario_codes[1], option_code="A"),
                ],
            ),
            db=self.db,
        )

        self.assertEqual(submitted.test_run_id, started.test_run_id)
        expected_gene_count = (
            self.db.query(Gene).filter(Gene.version_id == "v_test").count()
        )
        self.assertEqual(len(submitted.top_genes), min(3, expected_gene_count))
        self.assertEqual(submitted.quran_values, [])
        self.assertEqual(submitted.prophet_traits, [])
        self.assertEqual([item.channel for item in submitted.activation_items], ["behavior", "reflection", "social"])

        self.assertEqual(self.db.query(Answer).filter(Answer.test_run_id == started.test_run_id).count(), 2)
        self.assertEqual(
            self.db.query(ComputedGeneScore).filter(ComputedGeneScore.test_run_id == started.test_run_id).count(),
            3,
        )
        self.assertEqual(
            self.db.query(ComputedModelMatch).filter(ComputedModelMatch.test_run_id == started.test_run_id).count(),
            1,
        )
        completed_run = self.db.query(TestRun).filter(TestRun.id == started.test_run_id).first()
        self.assertIsNotNone(completed_run.submitted_at)
        self.assertEqual(completed_run.status, "completed")

        feedback_response = submit_journey_feedback(
            payload=JourneyFeedbackRequest(test_run_id=started.test_run_id, judged_score=4),
            db=self.db,
        )
        self.assertEqual(feedback_response.judged_score, 4)
        self.assertIsNone(feedback_response.selected_activation_id)

        selected_activation_id = submitted.activation_items[0].advice_id
        feedback_response = submit_journey_feedback(
            payload=JourneyFeedbackRequest(
                test_run_id=started.test_run_id,
                judged_score=5,
                selected_activation_id=selected_activation_id,
            ),
            db=self.db,
        )
        self.assertEqual(feedback_response.judged_score, 5)
        self.assertEqual(feedback_response.selected_activation_id, selected_activation_id)

        feedback_row = self.db.query(Feedback).filter(Feedback.test_run_id == started.test_run_id).first()
        self.assertEqual(feedback_row.judged_score, 5)
        test_run = self.db.query(TestRun).filter(TestRun.id == started.test_run_id).first()
        self.assertEqual(test_run.selected_activation_id, selected_activation_id)

    def test_start_rotates_between_scenario_sets_per_run(self):
        first_run = start_journey(payload=JourneyStartRequest(version_id="v_test"), db=self.db)
        second_run = start_journey(payload=JourneyStartRequest(version_id="v_test"), db=self.db)

        first_codes = [item.scenario_code for item in first_run.scenarios]
        second_codes = [item.scenario_code for item in second_run.scenarios]
        self.assertIn(first_codes, [["S01", "S02"], ["B01", "B02"]])
        self.assertIn(second_codes, [["S01", "S02"], ["B01", "B02"]])

    def test_feedback_rejects_activation_not_offered_for_test_run(self):
        started = start_journey(payload=JourneyStartRequest(version_id="v_test"), db=self.db)
        scenario_codes = [item.scenario_code for item in started.scenarios]
        submit_journey_answers(
            payload=JourneySubmitAnswersRequest(
                version_id="v_test",
                test_run_id=started.test_run_id,
                answers=[
                    JourneyAnswerSubmission(scenario_code=scenario_codes[0], option_code="A"),
                    JourneyAnswerSubmission(scenario_code=scenario_codes[1], option_code="A"),
                ],
            ),
            db=self.db,
        )

        with self.assertRaises(HTTPException) as ctx:
            submit_journey_feedback(
                payload=JourneyFeedbackRequest(
                    test_run_id=started.test_run_id,
                    judged_score=4,
                    selected_activation_id="ACT_OTHER",
                ),
                db=self.db,
            )

        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("was not offered for this test_run", str(ctx.exception.detail))

    def test_cancel_marks_started_run_cancelled(self):
        started = start_journey(payload=JourneyStartRequest(version_id="v_test"), db=self.db)
        cancelled = cancel_journey(
            payload=JourneyCancelRequest(test_run_id=started.test_run_id),
            db=self.db,
        )
        self.assertEqual(cancelled.status, "cancelled")
        self.assertEqual(self.db.query(TestRun).filter(TestRun.id == started.test_run_id).first().status, "cancelled")

    def test_cancel_does_not_override_completed_status(self):
        started = start_journey(payload=JourneyStartRequest(version_id="v_test"), db=self.db)
        submit_journey_answers(
            payload=JourneySubmitAnswersRequest(
                version_id="v_test",
                test_run_id=started.test_run_id,
                answers=[
                    JourneyAnswerSubmission(scenario_code="S01", option_code="A"),
                    JourneyAnswerSubmission(scenario_code="S02", option_code="A"),
                ],
            ),
            db=self.db,
        )

        cancelled = cancel_journey(
            payload=JourneyCancelRequest(test_run_id=started.test_run_id),
            db=self.db,
        )
        self.assertEqual(cancelled.status, "completed")
        self.assertEqual(self.db.query(TestRun).filter(TestRun.id == started.test_run_id).first().status, "completed")


if __name__ == "__main__":
    unittest.main()
