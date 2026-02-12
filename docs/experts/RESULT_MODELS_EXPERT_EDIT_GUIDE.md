# Result Models Expert Edit Guide (Genes, Archetypes, Values, Traits, Activation)

Last updated: 2026-02-12

## 1) Purpose

This guide is for experts who want to improve the result system content (not question sets).

It explains:
- what each result block means,
- which CSV files control it,
- what is safe to edit,
- and what rules must be respected to avoid breaking imports or runtime scoring.

## 2) Result blocks (what users see after submit)

The journey result response includes 5 blocks:
1. `top_genes`
2. `archetype_matches`
3. `quran_values`
4. `prophet_traits`
5. `activation_items`

This guide covers the content behind those blocks.

## 3) Files experts may edit

### Genes (base layer)
- `seed/genes_v2.csv`
  - columns: `gene_code,name_en,name_ar,desc_en,desc_ar`

### Archetype models
- `seed/sahaba_models_v2.csv`
  - columns:
    - base: `version_id,model_code,name_en,name_ar,summary_ar`
    - plus one numeric column for each gene code

### Quran values + gene weights
- `seed/quran_values.csv`
  - columns: `quran_value_code,name_en,name_ar,desc_en,desc_ar,refs`
- `seed/quran_value_gene_weights_v2.csv`
  - columns: `quran_value_code` + one numeric column for each gene code

### Prophet traits + gene weights
- `seed/prophet_traits.csv`
  - columns: `trait_code,name_en,name_ar,desc_en,desc_ar,refs`
- `seed/prophet_trait_gene_weights_v2.csv`
  - columns: `trait_code` + one numeric column for each gene code

### Activation advice and triggers
- `seed/advice_items_v2.csv`
  - columns: `version_id,advice_id,channel,advice_type,title_ar,title_en,body_ar,body_en,priority`
- `seed/advice_triggers_v2.csv`
  - columns: `version_id,trigger_id,trigger_type,gene_code,model_code,channel,advice_id,min_score,max_score`

## 4) Hard constraints (must follow)

### 4.1 Gene code stability
- Do not rename or delete existing `gene_code` values unless engineering is included in the change.
- Adding/removing a gene requires synchronized updates in many files (models + weight matrices + possibly triggers).

### 4.2 Matrix completeness
- In `sahaba_models_v2.csv`, `quran_value_gene_weights_v2.csv`, and `prophet_trait_gene_weights_v2.csv`:
  - every existing gene code must exist as a column,
  - unknown extra gene columns are not allowed.

### 4.3 Reference integrity
- Every `advice_triggers_v2.csv.advice_id` must exist in `advice_items_v2.csv`.
- `gene_code` in triggers must exist in `genes_v2.csv` (if used).
- `model_code` in triggers must exist in `sahaba_models_v2.csv` (if used).

### 4.4 Score range integrity
- In triggers: `min_score <= max_score` is required.

## 5) Recommended modeling rules (quality, not strict parser rules)

### 5.1 Numeric ranges
- Archetype gene vectors: keep values in `0..1` for interpretability.
- Quran/Prophet gene weights: keep values in `0..1`.
- Avoid negative values unless intentionally designed and reviewed.

### 5.2 Normalization style
- For each Quran value / Prophet trait row, prefer weight sums close to `1.0`.
  - This is not mandatory in code, but it makes scores easier to compare.

### 5.3 Coverage and balance
- Ensure all genes have meaningful participation in each matrix (avoid always-near-zero columns).
- Avoid one gene dominating all rows unless conceptually justified.

## 6) How each block is computed (simple)

### 6.1 `top_genes`
- Built from user selected options and `option_weights_v2.csv` (question set side).
- Ranked by raw score, normalized to `0..100`.

### 6.2 `archetype_matches`
- Cosine similarity between user gene vector and each archetype vector in `sahaba_models_v2.csv`.
- Top matches are returned.

### 6.3 `quran_values` / `prophet_traits`
- Weighted sum against normalized user gene scores:
  - `row_score = Σ(user_gene_normalized[g] * row_weight[g])`
- Top rows are returned by score.

### 6.4 `activation_items`
- Triggers are evaluated against top genes/model and score ranges.
- One item is selected per channel: `behavior`, `reflection`, `social`.
- If no trigger matches a channel, fallback uses highest-priority item in that channel.

## 7) Current v2 trigger pattern (important)

Current seed pattern:
- 60 triggers total
- all are `TOP_GENE`
- 20 genes × 3 channels
- score range: `0..100`

This means activation currently depends on dominant gene, not model-based logic.

## 8) Safe edit scope for non-engineering experts

Safe without schema/logic changes:
- improve wording in:
  - `genes_v2.csv` names/descriptions,
  - `quran_values.csv` names/descriptions/refs,
  - `prophet_traits.csv` names/descriptions/refs,
  - `advice_items_v2.csv` titles/bodies.
- tune numeric values inside existing matrix structures.
- adjust trigger ranges/priorities while keeping valid references.

Needs engineering coordination:
- adding/removing/renaming gene codes,
- introducing new trigger logic types at scale,
- changing expected activation channels.

## 9) Minimal edit template

Use this checklist when delivering updates:
1. List files changed.
2. State whether any `gene_code`, `model_code`, `quran_value_code`, or `trait_code` was added/removed.
3. For each matrix file, confirm all gene columns are present.
4. For `advice_triggers_v2.csv`, confirm:
   - all `advice_id` references exist,
   - all `gene_code`/`model_code` references exist,
   - every row has `min_score <= max_score`.
5. Provide a short rationale for major numeric changes.

