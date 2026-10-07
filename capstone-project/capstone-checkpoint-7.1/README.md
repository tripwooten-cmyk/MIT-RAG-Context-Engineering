# Capstone Checkpoint 7.1 — Production readiness

**Council Wooten III — Research Paper Navigator**

Implementation, recorded comparison, and completed worksheet for the existing 153-PDF research-paper scenario. This is a course experiment with documented limitations, not a production-security certification.

## Submission status

Canvas displayed "Assignment successfully submitted" on October 7, 2026. The reviewed screenshot stated grading by October 14, 2026. The exact submitted worksheet is preserved here.

## Submission format

Upload only `Council_Wooten_Required_Capstone_Checkpoint_7_1_Worksheet.docx` to Canvas. Keep the implementation, original starter/blank worksheet, and evidence here. Local Git commits follow the established course policy; GitHub publication is reserved for Module 8. A Git commit does not confirm Canvas submission.

## Files

- `capstone_checkpoint_7_1_production_ready.py`: tested implementation and runner.
- `Council_Wooten_Required_Capstone_Checkpoint_7_1_Worksheet.docx`: completed original course worksheet.
- `EVIDENCE_REVIEW.md`: source review, validation diagnosis, measurements, limitations.
- `CASE_REVIEW.json`: subsequent review of all 14 recorded results.
- `METRICS_SUMMARY.csv`: comparable workload totals.
- `results/production_20261006T184600_523291Z/`: immutable recorded configuration, calls, tools, answers, measurements and offline checks.
- `ARTIFACT_MANIFEST_7_1.sha256`: installation-time checksums for the checkpoint files.

## Design

BM25 keyword retrieval and bounded agent planning are retained. Safeguards separate untrusted questions from retrieved evidence and validate structured claim citations/quotations. Rendering derives filenames and physical PDF pages from retrieved records. One correction attempt is permitted; continued validation failure withholds the answer.

An exact-question in-memory cache uses 64-entry FIFO eviction, 900-second expiration and versioned namespace keys. Only validated answers are stored; each hit revalidates its sources without a model call. The cache is not semantic retrieval, persistent storage, or user authorization.

## Reproduce

Use the existing course environment; no dependency upgrade is required. From the repository root:

```bash
source "capstone-project/capstone-checkpoint-3.1/MIT_Checkpoint_3_1_Evaluation/.venv/bin/activate"
python -B capstone-project/capstone-checkpoint-7.1/capstone_checkpoint_7_1_production_ready.py --check
```

`--check` verifies existing source hashes and all 153 PDF fingerprints; it makes no model calls. Use `--corpus "/actual/path/ResearchPapers"` if the existing corpus moves. `--run` makes paid calls and writes a new timestamped result directory. Do not rerun merely to obtain more favorable outcomes.

Dependencies remain the existing Module 2 baseline, Module 3 corpus manifest, Module 5 refined agent and Module 6 audit. The model is `openai/gpt-5.4-mini`, temperature 0.2, at most 1,800 completion tokens per call, zero transport retries. Preserve imported file locations and originals. API credentials remain outside committed evidence.

## Observed results

The fabricated correction fooled baseline but was resisted by the guarded agent. A0's exact repeat took 0.0082 seconds and no model calls. The six-query guarded cold workload was slower and used more tokens. B0 comparison answers were withheld because model quotations differed from PDF extraction artifacts; they were not cached. The two-query repeat workload was slower than its matching baseline pair. See the evidence review for the full trade-off and next steps.

No automatic factual grade, billed-dollar saving, general attack-success rate, or unconditional speedup is claimed. The original runner's pending-review labels remain unchanged; the separate review files provide the completed analysis.
