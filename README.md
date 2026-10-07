# MIT xPRO RAG and Context Engineering

**Student:** Council Wooten III
**Purpose:** Capstone checkpoints, implementation files, laboratory exercises, evaluation evidence, and supporting documentation for the MIT xPRO RAG and Context Engineering program.

## Repository status

This repository contains capstone work through Checkpoint 7.1. Completed checkpoints are saved in descriptive local Git commits. The established policy reserves GitHub remote publication and submission for Module 8. See individual checkpoint evidence and commit history for verification; repository files do not establish learning-platform submission.

## Capstone scenario

The selected scenario is the **Research Paper Navigator**, which evaluates methods for retrieving evidence from a corpus of AI and program-synthesis research papers.

## Completed checkpoints

### Checkpoint 1.1 — Baseline model behavior

This checkpoint evaluated model responses before retrieval was implemented.

Authoritative files:

- `capstone-project/capstone-checkpoint-1.1/Council_Wooten_Required_Capstone_Checkpoint_1_1_Worksheet.docx`
- `capstone-project/capstone-checkpoint-1.1/capstone_checkpoint_1_1_baseline_solution.py`
- `capstone-project/capstone-checkpoint-1.1/checkpoint_1_1_responses.log`

The original starter, blank worksheet, and pre-correction implementation are retained separately for provenance.

### Checkpoint 2.1 — BM25 baseline retrieval

This checkpoint implemented keyword retrieval using BM25 over the course-provided research-paper corpus.

Implementation evidence:

- 153 PDF research papers processed
- 6,059 readable page-level chunks created
- Top three BM25 results retrieved for each query
- Four representative queries evaluated
- Retrieval and console logs preserved

Authoritative files:

- `capstone-project/capstone-checkpoint-2.1/Council_Wooten_Required_Capstone_Checkpoint_2_1_Worksheet.docx`
- `capstone-project/capstone-checkpoint-2.1/capstone_checkpoint_2_1_baseline_retrieval_solution.py`
- `capstone-project/capstone-checkpoint-2.1/checkpoint_2_1_console_output.txt`
- `capstone-project/capstone-checkpoint-2.1/checkpoint_2_1_retrieval.log`

The original starter and blank worksheet are retained separately for provenance.


### Checkpoint 3.1 — Evaluation infrastructure and baseline diagnosis

The unchanged Research Paper Navigator baseline was evaluated using four
saved answers and five constructed evaluator-validation cases through
MIT's RAGAS/OpenRouter workflow.

- Original correctness: 3/4 baseline answers passed.
- Refined evidence-and-attribution metric: 2/4 passed.
- Defects detected: original 2/4; refined 3/4.
- Both metrics accepted the supported control and missed the wrong citation.
- Q4 abstention received conflicting verdicts; these were preserved.
- These small-sample results do not establish general accuracy.

Authoritative checkpoint folder:
`capstone-project/capstone-checkpoint-3.1/`

- Approved worksheet: `Council_Wooten_Required_Capstone_Checkpoint_3_1_Worksheet.docx`
- Evaluator: `MIT_Checkpoint_3_1_Evaluation/evaluate_research_papers.py`
- MIT reference scripts: `MIT_Checkpoint_3_1_Evaluation/reference/`
- Captured inputs: `MIT_Checkpoint_3_1_Evaluation/input/`
- Actual results and configuration: `MIT_Checkpoint_3_1_Evaluation/results/mit_eval_01/`

The evaluator imports the supplied MIT solution. Preserve that directory
structure. Input and code hashes are recorded in run_config.json.
The worksheet alone is uploaded for Checkpoint 3.1; repository materials
support the final Module 8 submission. Platform submission is not confirmed
by this Git commit.

## Dataset governance

Instructor-provided source datasets are not committed. The following are intentionally excluded:

- Research-paper PDF corpus
- Detailed email laboratory corpus
- Chroma vector databases
- Python virtual environment
- API credentials
- Generated caches
- Microsoft Word temporary files

This keeps the repository appropriately sized and prevents credentials, generated indexes, and duplicated course datasets from being published.

## Evaluation method

Each representative query is evaluated at two architectural layers:

1. **Retrieval:** Did the system retrieve the correct supporting evidence?
2. **Generation:** Did the model use the retrieved evidence correctly?

The governing diagnostic question is:

> Did the system receive the wrong evidence, or did it mishandle the correct evidence?

## Known baseline limitations

BM25 performs well with exact titles, distinctive terminology, and direct keyword overlap. It is weaker with paraphrased queries, duplicate paper versions, and questions requiring evidence from multiple papers. These limitations support later evaluation of semantic, hybrid, metadata-filtered, and multi-stage retrieval.

## Verification

Repository integrity, solution syntax, and artifact fingerprints are checked with:

```bash
git fsck --full --strict
python -m py_compile \
  capstone-project/capstone-checkpoint-1.1/capstone_checkpoint_1_1_baseline_solution.py \
  capstone-project/capstone-checkpoint-2.1/capstone_checkpoint_2_1_baseline_retrieval_solution.py
shasum -a 256 -c ARTIFACT_MANIFEST.sha256
```

## Version-control policy

Each completed checkpoint receives a descriptive local Git commit. Files are inspected before staging and committing. The repository will remain local until the Module 8 GitHub submission requirement.

## Checkpoint 4.1 — Advanced retrieval evaluation

Scenario: Research Paper Navigator. Query decomposition and summed BM25
score fusion were evaluated over the same 153 PDFs and 6,059 readable
pages, using four questions and three final pages per answer.

Fresh comparison results:
- Original correctness: baseline 2/4; decomposition 3/4.
- Grounded correctness: baseline 1/4; decomposition 3/4.
- Mean retrieval-plus-answer time: 2.01 versus 3.19 seconds.
- Q4 improved; Q3 remained unresolved after fusion dropped needed evidence.

These are single-run judge results, not retrieval recall. Historical
Checkpoint 3.1 evidence remains separate.

Authoritative files under capstone-project/capstone-checkpoint-4.1:
- Council_Wooten_Required_Capstone_Checkpoint_4_1_Worksheet.docx
- capstone_checkpoint_4_1_advanced_retrieval_solution.py
- runs/comparison_01/comparison_results.json
- runs/comparison_01/comparison_summary.json
- runs/comparison_01/run_config.json

The solution imports the existing Checkpoint 2.1 baseline and Checkpoint
3.1 evaluation components. Preserve their repository locations.
Run configuration records code hashes, corpus hashes, prompts, models,
and package versions. The worksheet alone is uploaded for this checkpoint;
repository materials support Module 8. This commit does not confirm
learning-platform submission.

<!-- module-5-capstone -->
## Module 5: Agent-based RAG

[Checkpoint 5.1](capstone-project/capstone-checkpoint-5.1/README_CHECKPOINT_5_1.md) contains the completed worksheet, initial and refined implementations, recorded experiments, and evidence review for the 153-paper Research Paper Navigator. The worksheet is the checkpoint upload; code and evidence support the final capstone.
<!-- /module-5-capstone -->

## Module 6: Security and performance audit

`capstone-project/capstone-checkpoint-6.1/capstone_checkpoint_6_1_audit.py` audits the unchanged Module 5 refined agent on the existing research-paper corpus. Original audit evidence and worksheet remain in that checkpoint folder. Module 7 retains this audit and reuses its case definitions for a fresh baseline/guarded comparison.

## Module 7: Safeguards and conditional cache efficiency

[Checkpoint 7.1](capstone-project/capstone-checkpoint-7.1/README.md) contains the tested implementation, completed worksheet, source review, and 14 recorded results. It adds retrieved-citation/quotation validation and a versioned, expiring exact-question cache.

The fabricated-source attack was resisted and an eligible exact repeat avoided model calls. The guarded cold workload was slower and used more tokens, while strict quote checks withheld a useful comparison because of PDF extraction/text-format differences. These limitations and the matching-workload measurements are documented in the checkpoint evidence review. Upload the worksheet alone to Canvas; retain code and supporting evidence for Module 8.
