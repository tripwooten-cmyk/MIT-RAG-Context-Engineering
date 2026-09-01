# MIT xPRO RAG and Context Engineering

**Student:** Council Wooten III
**Purpose:** Capstone checkpoints, implementation files, laboratory exercises, evaluation evidence, and supporting documentation for the MIT xPRO RAG and Context Engineering program.

## Repository status

This repository is maintained locally through Module 2. It has no remote connection. A GitHub remote will be created and submitted only with the final capstone submission in Module 8.

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
