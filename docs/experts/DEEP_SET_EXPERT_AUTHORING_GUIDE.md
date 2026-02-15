# Deep Set Authoring Guide (External Experts)

Last updated: 2026-02-15

## 1) Purpose

This guide explains exactly how to create and submit one **Deep** question set for PersonaApp in a format ready for ingestion by our team.

## 2) What You Need to Submit

Submit either:
- one Excel file (`.xlsx`) with 3 sheets, or
- 3 CSV files.

Required tabs/files:
- `scenarios`
- `options`
- `weights`

## 3) Deep Set Overview

One Deep set must contain:
- `version_id`: always `v2`
- `scenario_set_code`: one unique set code (example: `deep_12`)
- scenarios: exactly **48**
- options per scenario: exactly **4** (`A`, `B`, `C`, `D`)

## 4) Allowed Gene Codes (Deep v2)

Use only these 20 gene codes in weights:

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

## 5) Deep Set Authoring Rules

### 5.1 Structural rules (required)
- Use one set code consistently in all rows (example: `deep_12`).
- Include exactly 48 scenarios.
- Set `order_index` as `1..48` with no gaps.
- Each scenario must have 4 options exactly: `A`, `B`, `C`, `D`.
- Every option must have at least one row in `weights`.
- `scenario_code` must be unique within the set (example pattern: `D12_01`, `D12_02`, ... `D12_48`).

### 5.2 Language rules (required)
- Provide both English and Arabic text.
- Arabic should be Modern Standard Arabic, natural, and without diacritics.
- Keep wording concise and behaviorally clear.
- Options should be meaningfully distinct from each other.

### 5.3 Weighting rules (required)
- Each weight row maps one option to one gene code and numeric weight.
- Positive weights are recommended (common pattern is `2`).
- Split weights are allowed (example: `ACHV=1` and `BALN=1` for the same option).
- Keep option totals balanced within each scenario.

### 5.4 Coverage rules (recommended)
- Across the full set, cover all 20 genes at least once.
- Balance contexts (family, friends, work/study, health, community, personal decisions).
- Avoid repeating near-identical scenarios.

## 6) Step-by-Step Workflow

1. Choose a new set code (example: `deep_12`).
2. Write 48 scenarios (EN + AR), each with `order_index`.
3. Write 4 options (`A/B/C/D`) for every scenario (EN + AR).
4. Assign weights for every option using only allowed gene codes.
5. Validate using the checklist in section 8.
6. Submit files to the PersonaApp contact person.

## 7) Templates and One Complete Example

### 7.1 `scenarios` template

Columns:
- `version_id,scenario_code,scenario_set_code,order_index,scenario_text_en,scenario_text_ar`

Example:

```csv
version_id,scenario_code,scenario_set_code,order_index,scenario_text_en,scenario_text_ar
v2,D12_01,deep_12,1,Your team asks you to lead a stressful task this week.,فريقك يطلب منك قيادة مهمة ضاغطة هذا الأسبوع.
```

### 7.2 `options` template

Columns:
- `version_id,scenario_code,option_code,option_text_en,option_text_ar`

Example:

```csv
version_id,scenario_code,option_code,option_text_en,option_text_ar
v2,D12_01,A,Accept and divide the work clearly.,أقبل المهمة وأقسم العمل بوضوح.
v2,D12_01,B,Accept but ask for support and check-ins.,أقبل المهمة وأطلب دعما ومتابعة دورية.
v2,D12_01,C,Delay decision until priorities are reviewed.,أؤجل القرار حتى أراجع الأولويات.
v2,D12_01,D,Decline and protect current commitments.,أعتذر للحفاظ على التزاماتي الحالية.
```

### 7.3 `weights` template

Columns:
- `version_id,scenario_code,option_code,gene_code,weight`

Single-gene option example:

```csv
version_id,scenario_code,option_code,gene_code,weight
v2,D12_01,A,ACHV,2
v2,D12_01,B,COMM,2
v2,D12_01,C,BALN,2
v2,D12_01,D,FREE,2
```

Split-weight option example (also valid):

```csv
version_id,scenario_code,option_code,gene_code,weight
v2,D12_01,A,ACHV,1
v2,D12_01,A,BALN,1
v2,D12_01,B,COMM,2
v2,D12_01,C,BALN,2
v2,D12_01,D,FREE,2
```

## 8) Final Checklist Before Submission

- 48 scenarios completed.
- `order_index` runs 1 to 48 with no gaps.
- Every scenario has 4 options (`A/B/C/D`).
- Every option has at least one weight row.
- No duplicate `scenario_code`.
- One consistent `scenario_set_code` across all tabs/files.
- Only approved deep gene codes are used.
- English and Arabic text are complete and clear.
