# Arabic-First Admin Analytics Plan

## 1. Goal and agreed scope

Replace the current technical-looking admin dashboard with one Arabic-first, right-to-left **"إحصائيات الاختبارات"** page for a non-technical administrator.

The page must answer only these questions:

1. كم اختباراً اكتمل؟
2. هل يرى المشاركون أن النتيجة دقيقة وتشبه شخصيتهم؟
3. هل التقييمات جيدة أم تحتاج إلى متابعة؟
4. هل استخدام الاختبارات يزيد أو يقل؟
5. هل يوجد فرق واضح بين الاختبار السريع والمتعمق؟

### Explicit non-goals for the first release

- Do not show legacy content-management counts (`users`, `questions`, `traits`, `idols`) on the dashboard.
- Do not show scenario-set codes, app-version IDs, database IDs, raw tables, or developer terminology.
- Do not delete the existing legacy CRUD pages or API endpoints. Remove them from the visible navigation only.
- Do not add user-level tracking or expose session identifiers.

## 2. Existing data and what it can support

### Runtime tables to use now

| Table | Relevant fields | Use in this dashboard |
|---|---|---|
| `test_runs` | `id`, `version_id`, `scenario_set_code`, `status`, `created_at`, `submitted_at`, `last_activity_at`, `selected_activation_id` | Count completed runs, determine the test type, and generate usage trends. |
| `feedback` | `test_run_id`, `accuracy_score` (1–10), `personality_match_score` (1–10), `created_at` | Calculate rating count, averages, and positive-rating percentage. |
| `app_versions` | `version_id`, `name`, `is_active` | Only needed later for internal version comparisons. |
| `answers` | `test_run_id`, `scenario_code`, `option_code` | Later answer-distribution diagnostics; it contains answers only after final submission. |
| `computed_gene_scores` | `test_run_id`, `gene_code`, `normalized_score` | Later result-distribution diagnostics. |
| `computed_model_matches` | `test_run_id`, `model_code`, `rank` | Later archetype-distribution diagnostics. |
| `advice_items`, `advice_triggers` | content metadata | Later activation-content analysis. |

### Legacy tables not used

`users`, `results`, `test_responses`, `questions`, `traits`, and `idols` belong to the earlier flow. Their empty counts in the current admin UI are misleading and must not appear in the new analytics page.

### Important data limitations

- A test run is marked `completed` only when `/journey/submit-answers` succeeds. This is the authoritative definition of a **completed test**.
- The first successful submission is the completion event. `/journey/submit-answers` must not overwrite a non-null `submitted_at` on retries or repeat requests, so completed tests cannot move between analytics periods.
- `started` and `cancelled` run states exist, so a high-level completion funnel is possible later.
- Answers are stored only at final submission. An unfinished run therefore has no answer/progress record; the current schema cannot identify the exact question where somebody left.
- Preview journeys do not write normal `test_runs` data and must be excluded naturally by querying persisted runs only.

## 3. First-release user experience

### Navigation and language

- Keep the public login URL: `/admin`.
- Keep the dashboard URL: `/admin/dashboard`.
- Show one sidebar item only: **إحصائيات الاختبارات**.
- Keep the old routes working but remove their links from the sidebar:
  - `/admin/questions`
  - `/admin/idols`
  - `/admin/traits`
- Arabic is the default, document direction is `rtl`, and every visible admin string is Arabic.
- English can be added later as a language toggle; it is not a first-release requirement.

### Date filter

At the top of the page show three buttons:

- **آخر 7 أيام**
- **آخر 30 يوماً** — default
- **كل الوقت**

The frontend passes only the selected range key (`7d`, `30d`, or `all`). The server resolves the UTC boundaries and returns them as ISO 8601 timestamps. Display those dates in Arabic/local form in the UI.

### Five KPI cards

| Arabic label | Definition | Empty state |
|---|---|---|
| **الاختبارات المكتملة** | Count of `test_runs` where `status = completed` and `submitted_at` is in the selected period. | `لا توجد اختبارات مكتملة في هذه الفترة` |
| **عدد التقييمات** | Count of feedback rows whose `created_at` is in the selected period. | `لا توجد تقييمات بعد` |
| **متوسط دقة النتيجة** | Average `feedback.accuracy_score`, rounded to one decimal, out of 10. | `—` |
| **متوسط توافق النتيجة مع الشخصية** | Average non-null `feedback.personality_match_score`, rounded to one decimal, out of 10. | `—` |
| **تقييمات الدقة الإيجابية** | Percentage of feedback rows with `accuracy_score >= 7`, rounded to nearest whole percent. Show the supporting count, for example `18 من 25`. | `—` |

Do not label an average as overall “satisfaction”: the product collects two distinct ratings and the labels must preserve their meaning.

### Clear status summary

Below the cards show one small, non-technical summary card titled **حالة التجربة**. It uses the accuracy-rating average only:

| Rule | Arabic message |
|---|---|
| Fewer than 10 accuracy ratings in the selected period | **لا توجد تقييمات كافية للحكم على جودة النتائج بعد.** |
| Average >= 8 | **تقييم دقة النتائج جيد جداً في هذه الفترة.** |
| Average >= 6 and < 8 | **تقييم دقة النتائج مقبول ويستحق المتابعة.** |
| Average < 6 | **تقييم دقة النتائج يحتاج إلى تحسين.** |

The message is descriptive, not a claim of scientific validity.

### One usage trend

Show a compact bar chart titled **الاختبارات المكتملة خلال الفترة**:

- Group by day for 7 or 30 days.
- Group by week for `كل الوقت` when the period spans more than 90 days.
- Data point = completed runs by `submitted_at`.
- Show zero-value day or week buckets so an absence of activity is visible.
- Mark the current, incomplete day or week as **حتى الآن** and style it distinctly. Do not present that partial bucket as evidence of an increase or decline relative to complete buckets.
- Use simple in-app bars/SVG; do not introduce a chart library for this one chart.

### Optional quick/deep comparison

Show this small section only when both journey types have at least one completed test in the selected period.

Title: **مقارنة أنواع الاختبارات**

| Shown label | Derived definition | Values shown |
|---|---|---|
| **الاختبار السريع** | `version_id` starts with `v1` | completed tests, average accuracy rating for those completed tests |
| **الاختبار المتعمّق** | `version_id` starts with `v2` | completed tests, average accuracy rating for those completed tests |

No scenario-set or version code is shown. If the version taxonomy changes, centralize this mapping in one backend helper rather than duplicating it in the frontend.

## 4. Backend contract and implementation design

### Endpoint

Add `GET /api/v1/admin/analytics` and migrate the dashboard page to it. Keep the existing `/api/v1/admin/stats` endpoint unchanged in this release so existing clients and admin-key verification continue to work.

Query parameter:

```text
range: "7d" | "30d" | "all", optional (default: "30d")
```

The server derives half-open UTC period boundaries: `from <= timestamp < to`. `7d` and `30d` include the current UTC day and the preceding 6 or 29 calendar days; `to` is midnight at the start of the next UTC day. `all` starts at midnight on the UTC day of the earliest persisted `TestRun.created_at`. If there are no test runs, `all` uses the current UTC day as `from`. The API response always returns the resolved `from` and exclusive `to` timestamps. Do not accept arbitrary client date ranges in the first release.

Response shape (names are internal; visible labels remain Arabic in the frontend):

```json
{
  "period": { "from": "2026-07-01T00:00:00Z", "to": "2026-07-19T00:00:00Z", "bucket": "day" },
  "completed_tests": 42,
  "feedback_count": 18,
  "avg_accuracy_score": 7.4,
  "avg_personality_match_score": 8.1,
  "positive_accuracy_feedback": { "count": 14, "percentage": 78 },
  "completion_trend": [
    { "date": "2026-07-01", "completed_tests": 3, "is_partial": false }
  ],
  "by_journey_type": [
    { "journey_type": "quick", "completed_tests": 31, "avg_accuracy_score": 7.2 },
    { "journey_type": "deep", "completed_tests": 11, "avg_accuracy_score": 7.9 }
  ]
}
```

### Query rules

- Use database aggregates (`COUNT`, `AVG`, conditional `COUNT`) and grouped date queries. Do not load all rows into Python.
- Every timestamp filter uses the same half-open rule: `timestamp >= from` and `timestamp < to`.
- `completed_tests` and the trend query filter `TestRun.status == 'completed'` and `TestRun.submitted_at` in the period.
- Feedback KPI metrics filter `Feedback.created_at` in the period. A rating is included even if it was submitted after the test completion date; this matches the user-facing phrase “ratings received in this period.”
- The type comparison is completion-cohort based. Both the completed count and average accuracy use `TestRun.submitted_at` in the selected period. Join `Feedback` to those runs without filtering `Feedback.created_at`, and return a `null` average when completed runs in that cohort have no feedback.
- Return zero-filled trend buckets. Generate the requested date sequence in Python and merge it with the grouped query results.
- Set `is_partial = true` only for the final bucket when it contains the current UTC time; all earlier buckets are complete.
- Always return stable keys, empty arrays, and `null` averages for no-data cases; never make the UI infer missing values.

### Schema and index work

Add one Alembic migration before enabling date-filtered production analytics:

- `test_runs(submitted_at)` index for completed-test counts and trends.
- `feedback(created_at)` index for rating metrics.
- Consider `test_runs(status, submitted_at)` instead of the single submitted index after checking `EXPLAIN ANALYZE` against production-like data. Use the simpler single-column index unless the compound index is demonstrably needed.

No new table or personally identifiable data is required for the first release.

### Files expected to change

- `backend/app/api/admin.py` — new analytics endpoint and aggregate queries.
- `backend/app/api/journey.py` — preserve the first non-null `submitted_at` on repeat submissions.
- `backend/app/schemas/admin.py` — analytics response models.
- `backend/alembic/versions/<new_revision>_add_admin_analytics_indexes.py` — date indexes.
- `frontend/src/services/adminApi.ts` — typed analytics request.
- `frontend/src/types/admin.ts` — analytics types.
- `frontend/src/pages/admin/AdminDashboard.tsx` — replace the current content with the Arabic dashboard.
- `frontend/src/pages/admin/AdminLayout.tsx` — Arabic header, RTL-aware layout, only one visible navigation item.
- `frontend/src/pages/admin/AdminLogin.tsx` — Arabic-first login copy.
- `frontend/src/App.tsx` — retain routes; do not remove legacy pages in this change.

## 5. Delivery sequence for the implementing agent

1. Add backend response schemas and unit tests describing all metrics and empty states.
2. Preserve the first non-null `submitted_at` on repeat answer submissions and add a regression test.
3. Add the index migration and run it locally.
4. Implement `GET /admin/analytics` using aggregate SQLAlchemy queries; keep the old `/stats` endpoint untouched in this release.
5. Add the typed frontend API client and replace the dashboard UI with the Arabic-first layout.
6. Simplify the sidebar and localize the login page; preserve the hidden legacy routes.
7. Run backend tests, frontend tests/build, and manually check the three date filters in Arabic RTL, including the partial-bucket treatment.
8. Deploy only after verification against production-like data. Confirm the dashboard never exposes session IDs or raw scenario/version codes.

## 6. Acceptance criteria for the first release

- `/admin` and `/admin/dashboard` are Arabic and RTL by default.
- The visible navigation contains only **إحصائيات الاختبارات** and a public-site link/logout action.
- The dashboard contains exactly five KPI cards, one status summary, one completed-tests trend, and the conditional two-row comparison.
- The dashboard has no content-management counts or raw scenario-set tables.
- `7 days`, `30 days`, and `all time` return correct, empty-safe results.
- All metric labels, no-data text, and error text are Arabic.
- Aggregate calculations are covered by backend tests, including empty `all` data, half-open date boundaries with fractional seconds, null personality ratings, completion-cohort ratings, mixed quick/deep data, and partial day/week buckets.
- Retrying `/journey/submit-answers` never changes the run's first `submitted_at` value.
- Existing admin content endpoints and legacy routes remain functional but are not linked from the sidebar.

## 7. Later phases (intentionally deferred)

### Phase 2 — Journey completion and engagement

Add an internal section, not the main dashboard, for:

- tests started, completed, cancelled, and completion rate;
- median completion time (`submitted_at - created_at`);
- activation-selection rate and most selected activation item.

Use existing `test_runs.status`, timestamps, and `selected_activation_id`. Define how to treat stale `started` runs before showing a cancellation rate; the cleanup task and 24-hour inactivity rule must be applied consistently.

### Phase 3 — Content and experiment quality

For internal content reviewers only, add filters for app version and scenario set, then show:

- completion and feedback comparison by version/set;
- top-gene distribution from `computed_gene_scores`;
- primary-archetype distribution from `computed_model_matches` where `rank = 1`;
- activation-item selection distribution.

Do not expose scenario-set IDs to the non-technical default dashboard. Add human-readable Arabic internal names before exposing these comparisons.

### Phase 4 — Question-level drop-off diagnostics

The current schema cannot measure abandoned-question position because answers are sent and saved only on final submission. Add explicit, privacy-preserving progress events before implementing this phase.

Minimal proposed table:

```text
journey_progress_events(
  id PK,
  test_run_id FK,
  scenario_code,
  event_type,             -- viewed | answered | exited
  created_at
)
```

Use it to show aggregate drop-off by question and time spent per step. Do not store free text, IP address, device fingerprint, or any direct identifier.

### Phase 5 — Operational reporting

Only after the dashboard proves useful:

- CSV export for aggregate tables;
- scheduled weekly Arabic summary for the administrator;
- threshold alerts for sustained rating decline or a sharp completion-rate drop;
- query-performance review and roll-up tables only if the aggregate queries become slow.
