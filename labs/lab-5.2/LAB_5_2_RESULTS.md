# Lab 5.2 — Implementation and Verification Results

Recorded: 2026-09-21
Learner: Council Wooten III

## Implementation and provenance

The working file was built from the corrected MIT starter. The two exercise
functions, retrieve_by_date and plan_node, were adapted from the supplied MIT
reference solution. MIT source files were preserved.

Working file:
Live_Guided_Virtual_Lab_5_2_starter/lab_5_2_tool_using_agent_working.py

Working SHA256:
436f635e7565182c8a7b358e8a6d2fe821cc2b0cc74a9990d7b6bbc2e337b9cb

Corrected starter SHA256:
6cabaf49e93c0366996c68624cd9cf08603baddf7dd1f47bf98281409aba24d7

The original starter contained a syntax error in the API-key help string.
The subsequently supplied MIT revision corrected that line and passed syntax
checks. No API key is included in this report.

Working-copy changes:
- Limit date retrieval to seven inclusive calendar days.
- Reject reversed date ranges.
- Sort date-tool file traversal.
- Report file-read failures rather than silently dropping evidence.
- Count clarification turns toward the existing iteration limit.

## Environment and data

Python 3.12.14; all 17 course dependency pins matched.
python-dateutil 2.9.0.post0 was also available.
Starter and reference datasets contained 7,894 matching email files.

The Lab 5.1 database passed a read-only SQLite quick check. Its langchain
collection contained 7,894 records with 1,536-dimensional embeddings.
Every stored filename and email body matched Lab 5.2's dataset.
Lab 5.2 subsequently loaded its existing database and performed live hybrid
retrieval successfully. This does not constitute an exhaustive vector-index audit.

## Local checks

Passed:
- Working-file Python syntax.
- Single-day lookup.
- Seven-day inclusive boundary, including an eight-day requested range.
- Reversed-range rejection.
- Zero results for January 1, 2014 in the actual corpus.
- Batch clarification records the question and increments the counter.

## Live observations

1. Empty date lookup:
   The agent selected by_date for January 1, 2014, returned zero emails,
   and answered without inventing results or repeating the lookup.

2. Topic change to the government project:
   Two successive runs each issued three hybrid-search queries in one retrieval
   round, then answered. Neither retained the earlier January 1 restriction.
   Both distinguished proposed remediation from confirmed completion.
   The second run supplied more specific failure details.
   These were same-session observations, not independent repeatability trials.

3. Ambiguous new project:
   The agent asked which project was intended.
   It clarified before searching, contrary to the supplied prompt's search-first
   guideline. The behavior was useful here, but illustrates that prompt
   instructions do not guarantee execution.

4. Clarification followed by a populated date lookup:
   After the user specified SandwichClip and May 2, 2017, the agent selected
   by_date, returned five emails, cited their filenames, and distinguished
   discussion of discontinuation from a finalized decision.

## Source verification

The second government-project answer was checked against these seven files:
- mail_02_12_15_1622.txt: destructive-testing failure due to inconsistent yield.
- mail_02_16_15_1637.txt: proposed remediation following prototype failures.
- mail_02_12_15_1625.txt: financial preparation for potential corrective actions.
- mail_02_20_15_1654.txt: proposed material/protocol changes and implementation timeline.
- mail_02_20_15_1655.txt: recommendations for enhanced testing parameters.
- mail_02_25_15_1672.txt: preparation to finalize a remediation proposal.
- mail_03_02_15_1684.txt: remaining presentation issues and proposal preparation.

These sources support the positive claims and do not confirm completed
corrective action. This is not proof that the entire corpus lacks a resolution.
The March 2 wording concerns presentation issues; it does not independently
establish that technical failures remained unresolved.

The SandwichClip answer cited:
mail_05_02_17_4409.txt through mail_05_02_17_4413.txt.
These correspond to the five emails previously inspected during Lab 5.1,
covering losses, a discontinuation meeting, and transition preparations.

## Limitations and status

All four actions were exercised: retrieve, by_date, clarify, and answer.
The planner still uses the MIT reference's limited JSON parsing and routing.
Repeated queries and date lookups are not deterministically blocked.
Planning sees only the first 20 accumulated emails.
Reaching the iteration limit forces an answer; it does not prove sufficiency.
Date lookup depends on correctly named files.
Exact costs and latency were not measured.
Reported decision explanations are model-generated, not proof of correct reasoning.
Results above summarize user-supplied terminal output; this report is not a raw
execution trace. Not every citation from the first government answer was checked.

The lab exercise and planned checks are complete, with the limitations recorded.
This is an educational implementation, not a production-readiness claim.
Capstone Checkpoint 5.1 implementation, evaluation, and worksheet remain separate work.
