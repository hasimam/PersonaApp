# Quick Set Authoring Guide (External Experts)

Last updated: 2026-02-15

## 1) Purpose

This guide explains exactly how to create and submit one **Quick** question set for PersonaApp in a format ready for ingestion by our team.

## 2) What You Need to Submit

Submit either:
- one Excel file (`.xlsx`) with 3 sheets, or
- 3 CSV files.

Required tabs/files:
- `scenarios`
- `options`
- `weights`

## 3) Quick Set Overview

One Quick set must contain:
- `version_id`: always `v1`
- `scenario_set_code`: one unique set code (example: `quick_11`)
- scenarios: exactly **12**
- options per scenario: exactly **4** (`A`, `B`, `C`, `D`)

## 4) Allowed Gene Codes (Quick v1)

Use only these 5 gene codes in weights:

| Code | English Name | Arabic Name |
|---|---|---|
| WIS | Wisdom / Hikmah | الحكمة |
| CRG | Courage / Shaja'ah | الشجاعة |
| HRM | Harmony / Insijam | الانسجام |
| DSC | Discipline / Iltizam | الانضباط |
| EMP | Mercy / Rahmah | الرحمة |

## 5) Quick Set Authoring Rules

### 5.1 Structural rules (required)
- Use one set code consistently in all rows (example: `quick_11`).
- Include exactly 12 scenarios.
- Set `order_index` as `1..12` with no gaps.
- Each scenario must have 4 options exactly: `A`, `B`, `C`, `D`.
- Every option must have at least one row in `weights`.
- `scenario_code` must be unique within the set (example pattern: `Q11_01`, `Q11_02`, ... `Q11_12`).

### 5.2 Language rules (required)
- Provide both English and Arabic text.
- Arabic should be Modern Standard Arabic, natural, and without diacritics.
- Keep wording concise and behaviorally clear.
- Options should be meaningfully distinct from each other.

### 5.3 Weighting rules (required)
- Each weight row maps one option to one gene code and numeric weight.
- Positive weights are recommended (common pattern is `2`).
- Keep option totals balanced within each scenario.

### 5.4 Coverage rules (recommended)
- Across the full set, cover all 5 genes at least once.
- Balance contexts (home, friends, work/study, stress, daily decisions).
- Avoid repeating near-identical scenarios.

## 6) Step-by-Step Workflow

1. Choose a new set code (example: `quick_11`).
2. Write 12 scenarios (EN + AR), each with `order_index`.
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
v1,Q11_01,quick_11,1,You have one free evening. What do you do first?,لديك مساء فارغ. ماذا تفعل أولًا؟
```

### 7.2 `options` template

Columns:
- `version_id,scenario_code,option_code,option_text_en,option_text_ar`

Example:

```csv
version_id,scenario_code,option_code,option_text_en,option_text_ar
v1,Q11_01,A,Call someone who needs support.,أتواصل مع شخص يحتاج دعما.
v1,Q11_01,B,Review priorities for tomorrow.,أراجع أولويات الغد.
v1,Q11_01,C,Set a fixed rest schedule.,أضع خطة راحة ثابتة.
v1,Q11_01,D,Try a new activity outside comfort zone.,أجرب نشاطا جديدا خارج منطقة الراحة.
```

### 7.3 `weights` template

Columns:
- `version_id,scenario_code,option_code,gene_code,weight`

Example:

```csv
version_id,scenario_code,option_code,gene_code,weight
v1,Q11_01,A,EMP,2
v1,Q11_01,B,WIS,2
v1,Q11_01,C,DSC,2
v1,Q11_01,D,CRG,2
```

## 8) Final Checklist Before Submission

- 12 scenarios completed.
- `order_index` runs 1 to 12 with no gaps.
- Every scenario has 4 options (`A/B/C/D`).
- Every option has at least one weight row.
- No duplicate `scenario_code`.
- One consistent `scenario_set_code` across all tabs/files.
- Only approved quick gene codes are used.
- English and Arabic text are complete and clear.
