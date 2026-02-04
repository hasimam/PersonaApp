# Multi-Set Scenario Generation Prompt (Arabic-First)

Use this prompt with any AI agent to generate additional 12-question scenario sets compatible with this project.

## Copy-Paste Prompt

```text
You are generating additional scenario sets for an existing Arabic-first self-discovery journey app.

Context:
- Existing stack expects 12 scenarios per set, each scenario has exactly 4 options (A/B/C/D).
- Each run should use one full 12-scenario set.
- Results map to these genes:
  - WIS (الحكمة)
  - CRG (الشجاعة)
  - HRM (الانسجام)
  - DSC (الانضباط)
  - EMP (الرحمة)

Your task:
Generate {{N}} new scenario sets (e.g., set_b, set_c, set_d), each with:
1) 12 scenarios (order_index 1..12)
2) 4 options per scenario (A/B/C/D)
3) Option weights compatible with existing scoring style

Important constraints:
- Arabic-first writing quality (natural, culturally grounded, clear MSA).
- Keep scenario purpose equivalent to the default set by order index (same psychological construct), but wording/context must be fresh.
- Keep tone practical and values-aware; do not produce religious rulings.
- Options must be behaviorally distinct and plausible.
- Write for broad inclusivity: suitable for teens/adults and mixed education levels.
- Use simple Arabic by default: short sentences, common words, minimal abstraction/jargon.
- Balance contexts across daily life (family, friends, study, work, neighborhood) to avoid office-only bias.
- Avoid assumptions about income, profession, or high formal education.
- Do not change schema/columns.

Output format (STRICT):
Return exactly 3 CSV blocks (no extra prose):
1) scenarios rows with columns:
   version_id,scenario_code,scenario_set_code,order_index,scenario_text_en,scenario_text_ar
2) scenario_options rows with columns:
   version_id,scenario_code,option_code,option_text_en,option_text_ar
3) option_weights rows with columns:
   version_id,scenario_code,option_code,gene_code,weight

Rules for IDs:
- version_id = v1
- scenario_set_code values should be: set_b, set_c, ...
- scenario_code format: B01..B12 for set_b, C01..C12 for set_c, etc.

Weighting rule:
- Replicate the same option-weight pattern used in the default set for each order_index:
  - A is Wisdom-leaning,
  - B is Courage-leaning,
  - C is Harmony/Empathy (depends on slot),
  - D is Discipline-leaning.
- Keep weights small integers matching existing style (mostly 2, occasionally split 1+1).

Quality checklist before final output:
- Exactly 12 scenarios per set.
- Exactly 4 options per scenario.
- All CSV rows consistent with schema.
- Arabic text has no broken punctuation/encoding.
- No duplicate scenario_code.
- Scenario wording is understandable for mixed age/education backgrounds.
- Context mix is diverse (not mostly corporate/workplace).
- Each option remains behaviorally distinct while still simple to read.
```

## Current Default Set (Sample Reference)

Source: `seed/scenarios.csv` (`scenario_set_code=default`)

| order_index | scenario_code | scenario_text_ar |
|---|---|---|
| 1 | S01 | في اجتماع متوتر، المجموعة تميل لقرار لا تقتنع به. |
| 2 | S02 | صديق يكرر خطأ يزعجك رغم أنك نبهته سابقاً. |
| 3 | S03 | يصلك تعليق غير واضح من مديرك: «طوّر أثرَك». |
| 4 | S04 | يبدأ خلاف في مجموعة محادثة والناس يساء فهمهم لبعض. |
| 5 | S05 | الوقت يضيق والمتطلبات تتغير باستمرار. |
| 6 | S06 | أحدهم ينتقدك أمام الآخرين. |
| 7 | S07 | تُعرض عليك فرصة جديدة لكنها تحمل مخاطر واضحة. |
| 8 | S08 | زميل متعثر ويؤخر الفريق كله. |
| 9 | S09 | تلاحظ ظلماً صغيراً لصالحك إن بقيت صامتاً. |
| 10 | S10 | شخصان مهمان لك على خلاف، وكلٌ يريدك في صفّه. |
| 11 | S11 | عليك اتخاذ قرار بمعلومات ناقصة. |
| 12 | S12 | تشعر بالإرهاق لكنك وعدت بتسليم شيء اليوم. |

Tip: keep each new set semantically equivalent to these 12 slots while varying contexts and phrasing.
