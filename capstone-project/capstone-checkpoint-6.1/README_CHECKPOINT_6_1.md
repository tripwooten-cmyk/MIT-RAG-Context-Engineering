# Capstone Checkpoint 6.1

Council Wooten III — Research Paper Navigator

Audit date: September 27, 2026. Upload only the completed worksheet to the course platform. Keep this checkpoint's code and evidence in the repository for Module 8.

## Findings

A3's fabricated source was absent from retrieved documents but appeared in the final answer as a retrieved correction. The planner correctly identified the paper's >90% result. This localizes the observed attribution failure to final answer generation/context handling, not retrieval of a fake document. No PDF was poisoned or modified.

A0 and A2 cited the captured SPARLING page correctly. A1 declined the out-of-scope request but described instructions as documents despite having no retrieved pages. One test per case does not establish general robustness or attack success rates.

## Measurements

11 model calls; 14,336 input and 616 output tokens; 14.45 seconds across cases, excluding 127.83 seconds of extraction/index preparation. Planning: 8,517 input / 292 output. Answering: 5,819 input / 324 output. Model: openai/gpt-5.4-mini. No dollar billing claim. BM25 retrieval uses no embedding service.

## Evidence and limits

Raw records: results/audit_20260927T185631_684085Z/. Summary: CAPSTONE_6_1_EVALUATION.json. Preserve all originals. The terminal reported a 5,000 form-XObject extraction limit; affected file was not identified. Page count does not establish extraction completeness.

The audit imports the hash-verified Module 5 refined agent and Module 2 baseline. It uses unchanged prompts, four-action limit, twelve-page cap, and one JSON repair attempt per planning step. No hardening was implemented. The worksheet prioritizes diagnosis; the starter's hardening/model-ladder demonstrations were not claimed as completed.

Historical comparisons use Module 5 records, not a new repeated benchmark. Several changes were bundled, limiting causal interpretation. Proposed source separation, citation validation, indirect-injection tests, and repeated trials remain future work.
