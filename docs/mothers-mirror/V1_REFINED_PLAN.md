# Mother's Miraat — refined first-version plan

Status: implemented three-practice private preview; updated 17 September 2026 against the current branch, `codex/mothers-miraat-preview`. The complete 30-day journey remains deferred.

Operational details and recorded deployment checks: [implementation status](IMPLEMENTATION_STATUS.md).

## Current implementation and changes since the proposal

- Implemented: home entry, `/mothers-mirror`, Arabic/English content for ages 6–12, twelve situations, four-area results with answer evidence, focus selection, three shared practices, daily progression, owned resume and deletion.
- Draft answers now save immediately in this browser, without an API request per selection. Reload restores the local draft; final submission sends all answers to the backend. Submitted results, focus and check-ins remain database-backed.
- The screen now follows the main journey's background, cards, buttons and progress treatment. Question counts come from the content; reserved status space avoids layout jumps. Deletion uses the shared confirmation modal.
- The isolated private preview serves React and FastAPI from one password-protected Vercel project with a separate Neon database. Login/logout use `Referrer-Policy: same-origin`; CSRF checks remain enabled.
- Current state sequence: `baseline → focus → practice (three cards) → preview_complete`. Review, closing, full-release publication and the other 25 practices are not implemented.
- This document describes repository behavior. The deployment recorded in the status document does not establish that every subsequent UI change is live.

Inputs: the owner's new “مرآتي: من الاختبار إلى رحلة النمو” brief, the recovered study and earlier concept (historical local planning material), and the current application code. This plan supersedes the earlier concept **for first-version scope**; the recovery remains historical evidence. Counts below are product decisions, not validated measurement requirements. Sections explicitly marked deferred describe the intended complete release, not current preview functionality.

## 1. The product decision

**A mother recognizes a response in herself, chooses something to practice, and returns to notice what changed.**

Original Mir'ati: situations → personal insight → characters and values → a suggested action.

Mother's Miraat: situations → parenting mirror → chosen focus → daily practice → another look.

The continuity is the familiar experience of recognition and a useful next step. Mother's Miraat adds ongoing practice. Character matching stays in the original journey; it is not needed to make parenting results meaningful.

### Where the sources meet

| Shared idea | First-version decision |
|---|---|
| Honest self-recognition | Everyday situations; describe answers, not a permanent mother type |
| Strength and growth together | One evidenced strength, one practice suggestion, four simple area cards |
| Islamic values lived through behavior | Each practice connects a value to an observable action |
| A personal path | Explain the suggested focus; mother can choose another |
| An ongoing practice journey | Three shared preview practices now; a common four-week program remains deferred |
| Notice change | Repeat assessment and response comparisons remain deferred |
| Familiar, simple Mir'ati experience | Same home, typography, colors, scenario cards, progress and result rhythm |

### Simplifications from the earlier study

- **12 situations, four choices each**, replacing the proposed 80 paired situations/160 ratings.
- **Four behavior areas**, replacing ten separate patterns and their recommendation matrix.
- **One shared program**, replacing ten complete journeys: three practices now, with the 30-day expansion deferred. Personalization initially means focus selection, explanation and review emphasis; daily content follows the same sequence.

No AI coach, inferred psychological roots, compulsory journaling, elaborate gates, or large content catalog in v1.

## 2. The four areas

| Area | Includes | A visible practice |
|---|---|---|
| أهدأ قبل أن أوجّه — Regulation | Pausing, noticing escalation, patience | Pause before responding |
| أسمع وأحتوي — Connection | Listening, warmth, understanding | Listen without interrupting |
| أضع حدودًا برحمة — Boundaries | Consistency, mistakes, repair | State the limit without labeling the child |
| أُربّي بالقدوة — Example | Responsibility, honesty, independence, apology | Model repairing one's own mistake |

These are broad lenses, not comprehensive measurement of every value in the brief. Faith, mercy and responsibility appear in practices; no score for faith or piety. Further areas can be introduced when sufficient questions and practices exist.

Confirmed first content audience: mothers thinking about **one child aged 6–12**, selected by the owner on 16 September 2026. No child's name, exact birth date or child profile required. The user keeps the same child in mind at review.

## 3. The experience, screen by screen

### Home → ابدئي مرآتك

- Add a main entry alongside the current quick/deep discovery choices.
- “افهمي استجابتكِ لطفلك، واختاري خطوة صغيرة للنمو.”
- Returning users see “واصلي مرآتك” or “خطوتك اليوم”.
- No prerequisite personality test or account creation for the pilot.

### Situations → 12 familiar cards

- One situation per screen; four believable responses, one selection.
- Prompt: “فكّري فيما حدث غالبًا خلال الأيام السبعة الماضية، لا في الإجابة المثالية.”
- Also allow “لم أمرّ بموقف مشابه”; it contributes no score.
- Save each answer in browser storage immediately; permit going back and correcting it. Submit the complete answer set once at the end. Failed submission retains the local draft; reloading a baseline journey overlays that draft without uploading it.
- Use the existing selected-card treatment and progress bar. Avoid making the socially desirable choice conspicuous through wording, length or fixed position.

### Result → مرآتك الآن

The first visible content is a short, answer-grounded message. Illustrative copy:

> في إجاباتكِ ظهرت مساحة للاستماع، بينما بدت بعض لحظات الغضب أصعب عليكِ. يمكنكِ أن تبدئي بالتوقف قبل الرد.

Below it:

- **قوة ظهرت في إجاباتك** — short description and an example linked to the relevant answer.
- **مساحة للنمو** — one suggestion and why it was suggested.
- Four small area cards; no radar chart or percentages in v1.
- “ما الذي تريدين التدرب عليه؟” — recommended focus preselected, all four available.

Do not invent a strength when answers do not support one. Use “ما لاحظناه” and mixed/insufficient-evidence wording instead. Avoid asserting that the child feels safe or that the mother is objectively a particular kind of parent.

### Complete-release plan → رحلة بخطوات صغيرة (deferred)

| Days | Theme | Purpose |
|---|---|---|
| 1–7 | أهدأ قبل أن أوجّه | Notice and regulate responses |
| 8–14 | أسمع وأحتوي | Practice warmth and listening |
| 15–21 | أضع حدودًا برحمة | Respond to mistakes with clear limits |
| 22–28 | أُربّي بالقدوة | Live values, responsibility and repair |
| 29 | ماذا تغيّر؟ | Short repeat mirror |
| 30 | خطوتي القادمة | Summarize and choose what to keep practicing |

The chosen focus remains visible throughout. Relevant practices are marked “مرتبطة بما اخترتِ التدرب عليه”. Be explicit that this is a shared program with a personal focus, not 30 uniquely generated tasks.

### Daily card → one doable action

Example of the card structure, not reviewed final parenting guidance:

| Card element | Example |
|---|---|
| Title | مساحة قبل الرد |
| Value | الصبر |
| Practice | في موقف مناسب اليوم، توقفي لحظة قبل الرد ولاحظي نبرة صوتكِ. |
| Words to try | أحتاج لحظة لأهدأ، ثم نتحدث. |
| Smaller version | لاحظي مرة واحدة أنكِ على وشك رفع صوتكِ. |

One check-in, not separate completion and emotion forms:

**جرّبتها بسهولة · جرّبتها بصعوبة · لم أجرّبها بعد · لم تتح الفرصة**

- Difficulty reveals the prewritten smaller version; she chooses whether to repeat or continue.
- No opportunity is not failure. No streak resets, red overdue cards or compulsory catch-up.
- One new practice per local calendar day. A missed day preserves the pending card; “30 days” means approximately 30 participation days and can take longer.
- No push notifications in the initial release. Re-entry from the home card must work reliably.

### Review → ماذا تغيّر؟ (deferred)

- Day 29 repeats eight anchors from the original twelve: two per area, same wording and seven-day reference window.
- Compare only those same answered anchors. Skipped answers are excluded from both sides of that comparison.
- If fewer than two paired answers remain in an area, say evidence is insufficient there.
- Emphasize the chosen focus. Show changed response descriptions, including no change or more difficulty.
- Practice completion is shown separately from changes in reported behavior.
- Copy says “بحسب إجاباتكِ” and acknowledges that weeks and circumstances differ. Repeated answers are not proof of improved child outcomes or a causal effect of the app.
- Day 30: keep practicing the chosen area, or choose another focus and repeat the available program. Clearly label repeated content. New specialized programs come later.

## 4. Scoring and recommendation rules

Use small, deterministic, reviewable rules rather than the original character-matching engine.

1. Each situation belongs to one primary area; each option has a draft editorial behavior-support weight from 0 to 2. Options may share weights. Skips have no weight.
2. Three situations per area. Require at least two answered situations to describe an area; otherwise request an optional additional answer or show “نحتاج مواقف أكثر”.
3. Average the valid weights for internal ordering. Equal scores remain ties; do not pretend to distinguish them.
4. Each area supplies draft descriptions for stronger support, mixed responses and growth opportunity. Provisional editorial bands: below 1, from 1 to below 1.5, and 1.5–2. Store thresholds with the content version; review with sample answer profiles before the pilot. These are editorial rules, not scientific cutoffs.
5. Offer the lowest sufficiently answered area as a focus. Explain using her selections. If tied, let her choose. If all areas have strong support, offer continued practice without fabricating a weakness.
6. Only describe a strength when the supporting band and answer examples justify it. No overall mother score, percentile, diagnostic label or spiritual grade.

The brief's 91%/57% displays illustrate a personal result. V1 preserves that result's meaning through language and evidence without presenting unsupported numerical precision.

## 5. Technical fit with the current application

Verified source locations:

| Current code | Reuse / adjustment |
|---|---|
| `frontend/src/App.tsx` | Original routes render `Journey`; `/mothers-mirror` renders `MothersMirror` |
| `frontend/src/pages/Journey.tsx` | Home entry offers start/continue based on the saved journey locator |
| `frontend/src/pages/MothersMirror.tsx` | Separate workflow with matching visual styles; no shared scenario-card extraction was needed |
| `frontend/src/components/ConfirmationModal.tsx` | Shared modal confirms or cancels journey deletion |
| `frontend/tailwind.config.js`, `frontend/src/index.css` | Reuse cream/slate/gold palette, Tajawal, rounded cards, soft shadows and button styles |
| `frontend/src/i18n/LanguageContext.tsx` | Reuse language and RTL behavior; seed content has Arabic/English fields |
| `frontend/src/services/api.ts` | Existing API client used directly by the Mother's Miraat page |
| `backend/app/db/session.py` | Same configured database, SQLAlchemy Base and request session |
| `backend/app/models/hybrid.py` | Existing content versioning and owned-run patterns inform the new tables |
| `backend/app/api/journey.py` | Reuse the ownership approach, not its 24-hour run expiry or gene/model scoring |
| `backend/alembic/versions/` | One additive migration; existing personality data remains structurally independent |

Architecture: existing React frontend + existing FastAPI service + existing PostgreSQL database. No additional service, database or AI dependency.

Keep the new workflow in a separate page and backend module. Extract only small UI pieces actually shared; do not turn the 1,100-line Journey component into a generic multi-product engine.

## 6. Implemented data model — four additive tables

| Table | Essential fields |
|---|---|
| `mother_content_releases` | id, version, status, content JSONB, published_at |
| `mother_journeys` | id, content_release_id FK, owner_token_hash, age_band, timezone, focus_code, status, current_day, next_available_at, created_at, updated_at, completed_at |
| `mother_assessments` | id, journey_id FK, kind (baseline now; review reserved), answers JSONB, result JSONB, submitted_at; unique journey + kind |
| `mother_checkins` | id, journey_id FK, day_number, outcome, repeat_requested, created_at, updated_at; unique journey + day |

- JSONB content is a typed, validated document: four areas with result descriptions, twelve situations and options/weights, eight reserved review-anchor IDs, three preview practices and scoring rules. The validator can check a 28-practice package, but full-release activation and review/closing behavior remain unavailable.
- Daily cards include a smaller alternative and area/value tags. Source-reference fields are not implemented. No dynamically generated religious claims.
- Use relational foreign keys for user records; JSONB keeps this small content package easy to author without many new lookup tables.
- New journeys bind to the latest activated `preview` release. Activated releases are immutable; existing journeys retain their original release. Review comparisons are deferred.
- Browser storage holds the journey locator/token and unsubmitted baseline answers. Selection and reload do not write draft answers to the backend. The backend still accepts draft saves, but the current UI only submits the complete baseline. Clear the local draft after successful submission; retain it on failure. The database is authoritative for submitted answers/results, focus and check-ins.
- Anonymous owner token follows the existing secure random token/hash approach. Require ownership on every read/write; never put the token in ordinary URLs or logs.
- Retain active journeys beyond 24 hours, including a missed week. Clearing browser storage loses automatic access in the pilot; say this plainly. Cross-device recovery/accounts can follow real pilot demand.
- Provide an owned delete action for the journey and its assessments/check-ins. No public sharing of parenting results in v1.

## 7. Current API contracts

Under `/api/v1/mothers-mirror` (using the application's configured API prefix):

| Method / path | Behavior |
|---|---|
| `POST /journeys` | Start against latest activated preview content; accept age band/timezone; return id, owner token and initial state |
| `GET /journeys/{id}` | Resume state, saved answers/result and available practice |
| `PUT /journeys/{id}/assessments/{kind}` | Baseline only: accept draft or submission, validate IDs/coverage and score on server; other kinds return 409 |
| `PUT /journeys/{id}/focus` | Confirm choice after baseline and before practice starts |
| `PUT /journeys/{id}/checkins/{day}` | Save/update outcome and repeat/continue choice; server advances eligible state |
| `POST /journeys/{id}/complete` | Deferred; no current endpoint |
| `DELETE /journeys/{id}` | Remove owned journey and dependent records |

Server enforces the preview sequence: baseline → focus → practice 1–3 → preview_complete. The final advancing check-in records completion directly. `not_yet` or an explicit repeat keeps the current card; other outcomes advance, including `no_opportunity`. The next card opens at local midnight and missed days do not skip cards. Invalid future-day writes are rejected. PUT retries are idempotent; duplicate taps cannot create duplicate answers/check-ins or advance twice. Client never supplies scores, content weights or trusted progression state. GET returns display content only, without option scoring weights.

## 8. Small initial content, clear expansion path

### Current private test: implemented working slice

Seeded **12 situations + 3 practice cards + draft result copy**. Content is explicitly not expert reviewed or scientifically validated. Backend test fixtures simulate time for daily progression; no clock bypass is exposed by the API and no review simulation is implemented.

The UI labels it a **three-practice preview** and shows an explicit ending after the third practice. The cards sample different areas; they do not represent days 1–3 of the deferred four-week curriculum. No review or improvement claim is shown.

### First complete release (deferred)

Expand the same package to **28 daily cards + day-29 review + day-30 closing**. Keep twelve baseline situations and eight reused anchors. No need for 300 exercises or a complete expert CMS.

### Adding content later

Author one versioned JSON file → validate IDs, references, translations, weights and coverage → import draft into the same database → preview with sample profiles → editorial review → publish a new immutable release.

The initial importer must be idempotent, reject changes to published releases, and check all 28 cards before full-release publication. Preview releases may have three cards with an explicit preview flag. A future admin editor writes this same structure. New age packages or specialized programs come before adding more measurement areas; a new area requires new assessment and review coverage.

## 9. Delivery status and remaining work

| Stage | Current status | Acceptance / next work |
|---|---|---|
| 1. Working private slice | Implemented | Home entry, assessment, results/focus, three cards, browser draft resume, database-backed submitted state and owned deletion |
| 2. Isolated online preview | Deployment and smoke checks recorded | Password-protected Vercel/Neon setup; see implementation status for operational details |
| 3. Complete content and review loop | Deferred pending feedback | Remaining 25 reviewed practices, eight-anchor comparison, closing, full-release publication and full lifecycle/regression checks |
| 4. Small user pilot | Feedback not recorded here | Observe 3–5 mothers, comprehension, usability and return behavior; do not infer parenting outcomes |

The earlier proposal's separate review-loop stage has not shipped. Deletion and test-only time simulation shipped with the preview. The 17 September request authorizes committing and pushing the current feature branch; it does not itself deploy the app or complete the deferred release.

### Focused engineering checks

- Scoring: ties, all-high, all-low, skips, insufficient coverage and no fabricated strength.
- Ownership: another token cannot read/write/delete a journey; raw tokens never persist in DB.
- Persistence: interrupted assessment, retry/double tap, refresh, week-long absence and version publication.
- Deferred review acceptance: paired anchors only, same content release, no comparison when coverage is insufficient.
- UX: mobile Arabic RTL and English; selected state, keyboard operation, reload/resume and failed-save messaging.
- Regression: original quick/deep journey, results and sharing remain intact alongside the separate Mother's Miraat page.

### Questions the pilot should answer

- “هل شعرتِ أن النتيجة تصف إجاباتكِ بصدق؟”
- “هل عرفتِ ما الخطوة التالية دون شرح؟”
- “هل كانت خطوة اليوم قابلة للتطبيق؟”
- Observe completion, confusing wording and return behavior. A small pilot tests usability and relevance, not scientific validity or parenting outcomes.

## 10. What makes this worth returning to?

| Moment | User value |
|---|---|
| A familiar situation | “هذا يحدث معي.” |
| A result grounded in my choices | “أفهم لماذا قيل لي هذا.” |
| Choosing my focus | “أعرف ما أريد أن أبدأ به.” |
| A small action and words to try | “أستطيع تجربة هذا اليوم.” |
| A difficult day with an easier alternative | “يمكنني المحاولة من جديد.” |
| A comparison of actual answers | “أرى ما تغير وما يزال صعبًا.” |

These are design hypotheses to test, not promises of engagement. The stable center is **مرآة صادقة → خطوة صغيرة → ملاحظة التغيّر**.
