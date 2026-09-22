# Capstone 5.1 evidence review

Council Wooten III — Research Paper Navigator — 2026-09-22

## Scope and method

Four development tasks, one fixed run and one initial-agent run per task, followed by one refined-agent run. Same corpus, model, temperature, answer prompt, and BM25 implementation. The agent can collect more pages than the fixed baseline. This is a qualitative, assistant-assisted source review; it is not an independent expert certification or a held-out accuracy benchmark. Original outputs are preserved, including mistakes.

## Results

| Task | Fixed | Initial agent | Refined agent |
|---|---|---|---|
| T0 SPARLING accuracy | Supported >90% statement and synthetic-domain qualifier | Same supported answer, extra calls | Same supported answer; invalid planner output recovered |
| T1 SPARLING versus Sketching | Requested sources missing; appropriately abstains | Retrieves both papers and supports comparison | Core comparison supported; specification quotations cite wrong page |
| T2 SYNQUID versus MYTH | Relevant comparison; at least one page citation error | Redundant page opens and action-limit stop | No repeated-page loop; normal answer stop; related-work evidence identified |
| T3 Sketching versus Learning to Infer Program Sketches | Misidentifies related papers as requested works | Invalid JSON, no retrieval, abstention | Retrieves intended papers; residual cross-paper attribution and page errors |

## Specific evidence checks

- T0: DBLP_journals_corr_abs-2302-01976.pdf, physical page 1, supports >90% accuracy on synthetic domains, up to feature permutation. It does not establish unrestricted real-world accuracy.
- T1 initial: SPARLING page 1 and DBLP_conf_aplas_Solar-Lezama09.pdf page 1 support end-to-end supervision versus programmer-supplied partial programs and correctness criteria.
- T1 refined: “Together with the sketch” and the parameterized/non-deterministic test-harness passages occur on physical page 2 of DBLP_conf_aplas_Solar-Lezama09.pdf. The answer cites page 1. Both pages were provided, making this a generation/citation failure despite available evidence.
- T2 fixed: “first to leverage general decidable refinement types” occurs on physical page 16 of DBLP_conf_pldi_PolikarpovaKS16.pdf, not page 15 as cited. Do not label the fixed answer citation-perfect.
- T2 initial: search already collected page 15; open_page requested it again, followed by two blocked identical requests. The four-step budget ended the loop. Previews omitted later page text; repeated requests could not expand those previews.
- T2 refined: one search then answer, using three pages. Evidence includes the SYNQUID paper and a related-work discussion in DBLP_conf_cav_BraggFRS21.pdf page 869. This is not independent retrieval of MYTH's original paper.
- T3 initial: call_01.json records incomplete JSON, finish_reason stop, 52 output tokens. The record does not support output-token exhaustion as the cause.
- T3 refined: the program-tree/DSL sketch definition is in Learning to Infer Program Sketches (DBLP_conf_icml_NyeHTS19.pdf page 2, continuing on page 3). The answer also places that wording under The Sketching Approach, citing APLAS page 1 and a PLDI 2005 paper. It additionally cites page 3 for the beginning of a definition on page 2. The central human-supplied versus neural-generated sketch contrast is supported, but attribution remains flawed.

## How Step 3 maps to the implemented changes

The system refinement changed the agent’s behavior through instructions, context, and a recovery step. Revised prompts guide separate title searches, paper-identity checks, avoidance of reopening collected pages, and acknowledgement of missing evidence. Supplying full collected-page text improves the information available for decisions. One JSON repair attempt changes the workflow when the model produces an incorrectly formatted instruction. Together these address the worksheet’s four examples. No model retraining or replacement of BM25 was performed.

These are implemented directions and controls, not a guarantee that the agent follows every instruction correctly. The observed improvements and remaining failures below must be considered together.

## Refinement and observed impact

Full collected-page context replaces 1,800-character planner previews. The prompt asks for separate title searches, identity checks, and no reopening collected pages. One repair call is permitted per invalid planning response; a second failure stops that task's planning. Offline tests exercised successful and failed repair and full-page context. In the live refined run, invalid outputs recovered in T0 and T1; T3 needed no repair. Thus the live run demonstrates recovery, but not a repeat of T3's exact malformed response.

Calls: fixed 4; initial agent 15; refined agent 16. Times: 14.72, 29.63, and 27.85 seconds respectively, excluding extraction/index construction. These timings are single-run observations. Increased context can increase token expense even when call counts are similar. No aggregate dollar claim is made. The initial and refined experiments together used 35 successful application model calls.

## Limitations and next work

Multiple changes were bundled, so improvements cannot be assigned to one change. No fresh baseline was rerun after refinement. No repeated-run statistics, full-corpus recall, comprehensive citation audit, or production reliability claim. The PDF parser reported a 5,000 form-XObject invocation limit; a 6,059-page count and zero unreadable files do not prove complete text extraction. The affected file was not identified in the terminal output. Prioritize exact citation validation, paper-identity checks, version deduplication, selective context expansion, and repeated/held-out tests. Human review remains necessary.
