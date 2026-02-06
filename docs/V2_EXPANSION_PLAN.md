# V2 Expansion Plan (Quick + Deep Journeys)

Last updated: 2026-02-06

## Scope
- Quick journey (v1): 5 genes, 12 scenarios (existing).
- Deep journey (v2): 20 genes, 48 scenarios, 30 Sahaba models.
- Add Quran values + Prophetic traits (top 5 each) in results for both journeys.
- Scenario sets: randomized selection per run (future‑proof for many sets).

## Decisions Locked
- v1 = quick, v2 = deep (separate versions).
- Random scenario set selection at journey start.
- Relative scoring within each run is acceptable.
- Deep activation content is gene‑specific (60 items: 20 genes × 3 channels).

## Data Assets (Status)
- v2 genes reference saved: `seed/genes_v2.csv` (DONE)
- v2 scenarios: `seed/scenarios_v2.csv` (DONE)
- v2 scenario options: `seed/scenario_options_v2.csv` (DONE)
- v2 option weights: `seed/option_weights_v2.csv` (DONE)
- v2 Sahaba models (30) (DONE)
- v2 activation items + triggers (60 + 60) (DONE)
- Quran values catalog + mappings (CATALOG DONE, MAPPINGS v2 DONE, v1 DONE)
- Prophetic traits catalog + mappings (CATALOG DONE, MAPPINGS v2 DONE, v1 DONE)

## Engineering Tasks
1. Seed pipeline update to support v2 content with `version_id` in all CSVs.
2. Journey start: select scenario set randomly within version.
3. Journey submit: compute top 5 genes (not 3).
4. Add Quran values + Prophetic traits scoring + response payload.
5. Frontend results UI updates for new sections.

## Next Input Needed
- Confirm if we should start integrating v2 into seed import and API/UX.

## Notes
- If we add v2 to seed import, we must add `version_id` to all seed CSVs.
- Keep “Sahaba archetypes” framed as inspirational profiles, not historical claims.
