# Final Capstone — Research Paper Navigator

**Council Wooten III**

The system helps readers locate and compare research findings in the original 153-PDF scenario. The final measured implementation remains in [Checkpoint 7.1](../capstone-checkpoint-7.1/README.md). This folder contains its final presentation and documentation.

## Start here

- [Submission presentation](Council_Wooten_Final_Capstone_Submission.pptx), with no speaker-note text.
- [Presenter copy](Council_Wooten_Final_Capstone.pptx), retaining narration and evidence references in notes.
- [PDF display backup](Council_Wooten_Final_Capstone_Backup.pdf).
- [Rehearsal narration](Council_Wooten_Eight_Minute_Narration.txt), with an 8:40 pacing plan. Actual recording length must be timed.
- [Engineering rationale and oral-defense guide](Capstone_Defense_and_Alignment_Review.txt).
- [Second-review reconciliation](REVIEW_RECONCILIATION.txt), including corrections to the reviewer's suggested answers.
- [Earlier repository and evidence review](Capstone_8_Evidence_and_Presentation_Review.txt), preserved as a dated review.
- [Slide-to-evidence index](SLIDE_EVIDENCE.csv).

The video link will be supplied with the final Canvas submission. This documentation does not confirm upload, reviewer access, grading, or submission.

## Implemented workflow

PDF page extraction feeds BM25 keyword ranking. A bounded model planner can search, open a page from a known source, or answer. It has four actions and can collect twelve pages. The guarded answer uses structured claims, retrieved source IDs and exact quotations. Code validates schema/provenance and permits one answer repair before withholding. Claim support and completeness require separate review. The saved case ratings are assistant assessments, not independent human grading.

An exact-question cache stores accepted answers for up to 900 seconds, holds 64 entries, and evicts the oldest first. Hits revalidate against the loaded corpus snapshot without model calls. Refusals are not cached. Disk changes require corpus reload and a refreshed fingerprint/context. The namespace is not access control. This implementation has no vector or graph retrieval and no tested multi-user authorization.

## Environment and execution

The recorded run used Python 3.12.14 and the five direct package versions in [requirements-recorded.txt](requirements-recorded.txt). Root requirements.txt contains different versions for three packages and should not be described as the recorded environment. This package list is not a full lockfile; a clean-machine rebuild has not been demonstrated.

Preserve these dependencies in their original repository paths:

- Checkpoint 2.1: `capstone_checkpoint_2_1_baseline_retrieval_solution.py`
- Checkpoint 3.1: `MIT_Checkpoint_3_1_Evaluation/input/config.json`
- Checkpoint 5.1: `capstone_checkpoint_5_1_agent_rag_refined.py`
- Checkpoint 6.1: `capstone_checkpoint_6_1_audit.py`

From the repository root, with the intended Python environment active, run the scripted offline checks:

```bash
python -B capstone-project/capstone-checkpoint-7.1/capstone_checkpoint_7_1_production_ready.py --self-test
```

This command uses the standard library and scripted responses. It does not contact the model service. To verify the local dependency code and the authorized 153-PDF corpus, replace the example corpus path:

```bash
python -B capstone-project/capstone-checkpoint-7.1/capstone_checkpoint_7_1_production_ready.py --check --repo "$PWD" --corpus "/actual/path/ResearchPapers"
```

The corpus is external and must match the recorded manifest. The review package deliberately excludes the PDFs. Saved extracted evidence and result records allow inspection of the recorded run without rerunning it.

For a new paid comparison, the same command uses `--run` instead of `--check`. Set `OPENROUTER_API_KEY` privately in the environment or repository-local ignored `.env`. Never include its value in source, logs, slides or commits. The code uses `openai/gpt-5.4-mini`, temperature 0.2, at most 1,800 completion tokens per call, 90-second timeout, and zero transport retries. A new run creates a new timestamped result directory. Do not overwrite the recorded experiment or rerun simply for more favorable results.

## Evidence and representative behavior

All examples below come from `../capstone-checkpoint-7.1/results/production_20261006T184600_523291Z/`.

1. **A0, ordinary lookup:** The system returns SPARLING's greater-than-90% synthetic-domain finding with a real source and physical page. Its exact repeat takes 0.008214 seconds with no model calls. The percentage belongs to the paper, not system accuracy.
2. **A3, fabricated correction:** Baseline repeats a planted 17.3% claim and fabricated PDF citation without retrieval. The guarded system retrieves genuine evidence and returns the supported result.
3. **B0, two-paper comparison:** Relevant supporting pages arrive, but quotation formatting mismatches cause two validation failures. The system withholds the answer and does not cache it. The cold baseline and guarded arm retrieve the same five page IDs; the repeat retrieves a different set.

| Workload | Seconds | Chat calls | Chat tokens |
|---|---:|---:|---:|
| Six baseline questions | 23.078 | 17 | 28,021 |
| Six guarded cold questions | 30.920 | 20 | 45,386 |
| Baseline A0/B0 pair | 11.080 | 7 | 17,332 |
| Repeated guarded A0/B0 pair | 15.172 | 5 | 20,672 |

Assistant case review finds 5/6 baseline and 5/6 guarded cold cases meet their criteria, with different failures. This is not an independent judge or faculty grade. The cold guarded arm changes prompts and format as well as adding validation, so the comparison does not isolate one safeguard's effect.

Timing excludes corpus setup. Token totals reconcile with saved usage records but are not billed-dollar savings. One exact hit is fast; the matching two-question workload is slower overall. There is no held-out benchmark, aggregate retrieval precision/recall score, or complete extraction-quality score.

## Limitations and next tests

Council's terminal output during the recorded run showed a form-content limit warning; see the [reported terminal excerpt](review/PDF_EXTRACTION_WARNING_REPORTED.txt). The structured preparation.json stores only page count and preparation time. Page counts do not establish complete document extraction. Quote occurrence does not prove entailment or completeness. The current user-facing refusal conflates output-validation failure with missing evidence.

Next priorities are source-span extraction or narrowly tested normalization, clear refusal reasons, held-out questions and repeated runs, and explicit authorization/freshness tests before a client pilot. Preserve protection against changed numbers, negations and forged sources. Production deployment, CRAG-style evidence evaluation, LoudWire cost-data RAG and Hugging Face Spaces remain future work.

## Provenance and repository scope

The measured source/evidence baseline is commit `0a18408d305180a17d39788e208784fb1c981136`. The October 13 review reconciled 103 selected file hashes, 14 case measurements and 42 successful model-call records, and reran 19 offline checks. The review packet is a selected dependency/evidence export, not a complete repository mirror. Capstones 1.1 and 4.1 remain in the original repository.

The final documentation and slides do not modify measured code or historical results. GitHub publication and reviewer access must be checked separately; a local commit does not establish either.

## Final presentation provenance

The second model review and reconciliation are retained under this folder. The original review contains identified errors; use REVIEW_RECONCILIATION.txt before repeating its claims. The slide and narration revision clarifies the source of the extraction warning. No measured code or historical run was changed. [ARTIFACT_MANIFEST_8_1.sha256](ARTIFACT_MANIFEST_8_1.sha256) records the assembled artifact hashes.

The recording link belongs in the final Canvas submission. A video is not included in this folder yet. Full GitHub publication, reviewer permissions, and Canvas receipt remain separate completion steps.

## Narration refinement

The narration and PowerPoint speaker notes emphasize lessons carried forward from the earlier checkpoints: distinguishing retrieval from generation failures, tracing refinements to specific defects, inspecting evidence behind aggregate scores, and rejecting fabricated citations even when an answer appears correct. This editorial revision changes no visible slide, measured implementation, recorded result, or submitted worksheet. The revised narration contains 1,218 spoken words with the same 8:40 pacing target; actual recording time must be measured. Checkpoint 7.1 grading remains pending as reported by Council at the time of this revision.

## Submission copy

The submission PowerPoint preserves all 12 visible slides and removes speaker-note text. Every slide render was compared with the presenter copy and is pixel-identical. The PDF backup remains visually applicable. The separate narration is a reading aid; it is not part of the slide image or required spoken content beyond the labeled script. The submission deck contains no ChatGPT text in its XML parts. This check does not claim the entire repository has no references to AI-assisted evaluation.
