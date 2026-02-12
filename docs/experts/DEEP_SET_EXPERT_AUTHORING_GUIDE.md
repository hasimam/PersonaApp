# Deep Set Authoring Guide (for Psychology, Social, and Language Experts)

Last updated: 2026-02-12

## 1) Purpose

This document explains:
- what one `deep` question set looks like in production,
- which core genes are scored,
- how answers map to results,
- and how to submit a new set in a format we can import directly.

Scope in this doc uses **v2 deep format** (48 scenarios per set).

## 2) One Real Set: `v2 / deep`

Current production-style deep set shape:
- `version_id`: `v2`
- `scenario_set_code`: `deep` (other sets follow same shape: `deep_01`, `deep_02`, ...)
- scenarios: **48**
- options per scenario: **4** (`A`, `B`, `C`, `D`)
- weight rows per option: **1** (in current v2 pattern)

Data files used by importer:
- `seed/scenarios_v2.csv`
- `seed/scenario_options_v2.csv`
- `seed/option_weights_v2.csv`

## 3) Core Genes We Evaluate

These 20 genes are scored in v2:

| Code | English Name | Arabic Name |
|---|---|---|
| LOVE | Love & Care | الحب والرعاية |
| ACHV | Achievement | الإنجاز |
| JOY | Happiness & Contentment | السعادة والرضا |
| FREE | Autonomy | الاستقلالية |
| SAFE | Safety & Security | الأمن |
| HLTH | Health & Wellness | الصحة والعافية |
| DIGN | Dignity & Respect | الكرامة والاحترام |
| JUST | Justice & Fairness | العدالة والمساواة |
| FRND | Friendship | الصداقة |
| LEARN | Learning & Knowledge | التعلم والمعرفة |
| SPIR | Meaning & Purpose | المعنى والغاية |
| FINC | Financial Stability | الاستقرار المالي |
| RECO | Recognition | التقدير والاعتراف |
| ADVN | Adventure & Challenge | المغامرة والتحدي |
| ARTS | Beauty & Art | الجمال والفن |
| FUN | Fun & Enjoyment | المرح والترفيه |
| COMM | Community & Belonging | الانتماء والمجتمع |
| AMBT | Ambition & Growth | الطموح والتطور |
| GRAT | Gratitude | الامتنان |
| BALN | Work-Life Balance | التوازن بين العمل والحياة |

## 4) How Questions and Answers Are Wired to Results

Pipeline per run:
1. A full scenario set is selected.
2. User answers each scenario with one option (`A/B/C/D`).
3. Each selected option adds weight to one or more genes from `option_weights_v2.csv`.
4. Gene raw scores are summed.
5. Normalized score per gene is computed as:
   - `normalized = (raw_score / max_raw_score_in_run) * 100`
6. Genes are ranked by raw score (descending), then code (deterministic tie-break).
7. API returns top genes (UI currently shows top 5; roles are assigned to first 3: dominant, secondary, support).

### Concrete Example (from `v2 / deep / D01`)

Scenario (`D01`):
- AR: `عائلتك تخطط لتجمع في عطلة نهاية الأسبوع لكنك تشعر بالإرهاق.`

Options and weights:
- `A`: `أحضر وأشارك بشكل كامل وأدعم الجميع بمحبة.` -> `LOVE +2`
- `B`: `أحضر لفترة قصيرة ثم أعود للراحة.` -> `JOY +2`
- `C`: `أبقى في المنزل لأستعيد طاقتي.` -> `HLTH +2`
- `D`: `أعتذر بلطف للحفاظ على وقتي الخاص.` -> `FREE +2`

## 5) Authoring Rules for New Deep Sets

Use these rules to keep new sets valid and easy to import:

### 5.1 Structural rules (required)
- `version_id` must be `v2`.
- One set must contain exactly **48 scenarios**.
- `order_index` must be `1..48` with no gaps.
- `scenario_set_code` should be new and unique (example: `deep_11`).
- Each scenario must have exactly 4 options: `A`, `B`, `C`, `D`.
- Each option must have at least 1 weight row in `option_weights_v2.csv`.
- All referenced `gene_code` values must exist in the 20-gene list above.
- Across a full set, all 20 genes should be covered at least once (strongly recommended baseline).

### 5.2 Language rules (required)
- Modern Standard Arabic (MSA), no diacritics.
- Natural app tone, short and clear sentences.
- Avoid robotic translation style.
- Keep options behaviorally distinct.
- Keep options in first-person style (recommended pattern starts with `أ...`).

### 5.3 Content design rules (recommended)
- Balance contexts: family, friends, work/study, health, community, personal decisions.
- Avoid repeating identical scenario logic with only minor wording changes.
- Keep options realistic for mixed age/education audiences.
- Avoid extreme or moralizing phrasing.

### 5.4 Weighting policy (important)
- `+2` is common in current `v2`, but not mandatory.
- An option can map to multiple genes (split weighting), for example:
  - Option A -> `ACHV +1`, `BALN +1`
- Keep weight totals comparable across options inside one scenario:
  - Recommended: each option totals to `2` points.
- Avoid negative weights unless intentionally designed and reviewed.
- Across all 48 scenarios, keep gene exposure reasonably balanced.

## 6) Easy Submission Format (what to send us)

Please submit **3 CSV files** (UTF-8):

1. `scenarios_v2.csv` rows:
   - `version_id,scenario_code,scenario_set_code,order_index,scenario_text_en,scenario_text_ar`
2. `scenario_options_v2.csv` rows:
   - `version_id,scenario_code,option_code,option_text_en,option_text_ar`
3. `option_weights_v2.csv` rows:
   - `version_id,scenario_code,option_code,gene_code,weight`

### Minimal Example (single scenario)

`scenarios_v2.csv`
```csv
version_id,scenario_code,scenario_set_code,order_index,scenario_text_en,scenario_text_ar
v2,D11_01,deep_11,1,Your team asks you to lead a stressful task this week.,فريقك يطلب منك قيادة مهمة ضاغطة هذا الأسبوع.
```

`scenario_options_v2.csv`
```csv
version_id,scenario_code,option_code,option_text_en,option_text_ar
v2,D11_01,A,Accept and divide the work clearly.,أقبل المهمة وأقسم العمل بوضوح.
v2,D11_01,B,Accept but ask for support and check-ins.,أقبل المهمة وأطلب دعما ومتابعة دورية.
v2,D11_01,C,Delay decision until priorities are reviewed.,أؤجل القرار حتى أراجع الأولويات.
v2,D11_01,D,Decline and protect current commitments.,أعتذر للحفاظ على التزاماتي الحالية.
```

`option_weights_v2.csv`
```csv
version_id,scenario_code,option_code,gene_code,weight
v2,D11_01,A,ACHV,2
v2,D11_01,B,COMM,2
v2,D11_01,C,BALN,2
v2,D11_01,D,FREE,2
```

Optional split-weight variant (also valid):
```csv
version_id,scenario_code,option_code,gene_code,weight
v2,D11_01,A,ACHV,1
v2,D11_01,A,BALN,1
v2,D11_01,B,COMM,2
v2,D11_01,C,BALN,2
v2,D11_01,D,FREE,2
```

## 7) Validation Checklist Before Sending

- Set has exactly 48 scenarios.
- Every scenario has 4 options (`A/B/C/D`).
- Every option has weight mapping.
- No duplicate `scenario_code`.
- Arabic is clear, natural, and no diacritics.
- `scenario_set_code` is new and consistent across all 3 files.
- All 20 genes appear at least once across the full set.
- Inside each scenario, option total weights are balanced (recommended: same total per option).

## 8) Sample Result Generation (for expert review)

Important:
- The user is scored against all 20 genes.
- API/UI currently show only the top 5 ranked genes.
- Non-shown genes are either lower-ranked or zero.

### Numeric example

Assume a user completes one full set and gets these raw scores:

| Rank | Role | Gene Code | Gene Name (AR) | Raw Score | Normalized |
|---|---|---|---|---:|---:|
| 1 | dominant | FREE | الاستقلالية | 18 | 100.00 |
| 2 | secondary | BALN | التوازن بين العمل والحياة | 16 | 88.89 |
| 3 | support | LOVE | الحب والرعاية | 14 | 77.78 |
| 4 | - | ACHV | الإنجاز | 12 | 66.67 |
| 5 | - | JOY | السعادة والرضا | 10 | 55.56 |

Normalization formula:
- `normalized = (raw_score / max_raw_score_in_run) * 100`
- In this example, `max_raw_score_in_run = 18`.

Decision/order logic:
1. Sum raw scores from selected option weights.
2. Rank genes by raw score descending.
3. If tied, break tie by gene code (deterministic ordering).
4. Assign roles to first 3 only:
   - #1 `dominant`
   - #2 `secondary`
   - #3 `support`
5. Return/display top 5 genes in order.

## 9) Internal Import Steps (for engineering)

After receiving expert content:
1. Place rows into root `seed/*_v2.csv`.
2. Run Arabic normalization (recommended):
   - `python3 scripts/normalize_ar_seed.py --in seed/scenarios_v2.csv --out seed/scenarios_v2.csv --fields scenario_text_ar --polish-phrases`
   - `python3 scripts/normalize_ar_seed.py --in seed/scenario_options_v2.csv --out seed/scenario_options_v2.csv --fields option_text_ar --polish-phrases`
3. Sync to backend seed pack:
   - `cp seed/scenarios_v2.csv backend/seed/scenarios_v2.csv`
   - `cp seed/scenario_options_v2.csv backend/seed/scenario_options_v2.csv`
4. Import:
   - `cd backend && source venv/bin/activate && python -m app.db.hybrid_seed_importer`
