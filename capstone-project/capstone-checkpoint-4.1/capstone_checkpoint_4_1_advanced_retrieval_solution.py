r"""Capstone Checkpoint 4.1 — Advanced Retrieval Implementation (starter).
Jupytext-style cell markers (# %% / # %% [markdown]) — runnable as a
plain script AND openable as cells in VS Code/PyCharm/Jupytext.
"""

# %% [markdown]
# # Capstone Checkpoint 4.1 — Advanced Retrieval Implementation
# **MO-LLM Module 4/Required Capstone Checkpoint (120 minutes)**
#
# ## What this checkpoint is
#
# This checkpoint advances your capstone system from a *single-pass* retriever to an
# **advanced retriever**. You will use the baseline retrieval system you built in
# Checkpoint 2.1 and evaluated in Checkpoint 3.1 to identify where single-pass retrieval
# falls short and apply the Module 4 techniques to fix it:
#
# - **Lab 4.1 — multistep retrieval (query decomposition):** Rewrite a complex
#   question into focused sub-queries, retrieve for each, and merge the results.
# - **Lab 4.2 — graph-based retrieval:** Organize your corpus as a graph of
#   relationships (citations, shared topics, links, same author/entity) and pull in
#   *related* documents a keyword/vector search would miss.
#
# You then **measure the improvement** against your 3.1 baseline. The graded
# deliverable is a **500-750 word written report** (final section). This script is a
# runnable demonstration of both techniques on a tiny sample corpus so you can see
# them work before adapting them to your real system.
#
# **Learning outcomes (Module 4):**
# 1. Identify common retrieval failures — e.g., complex multistep questions and too
#    much loosely-related context degrading the answer.
# 2. Explain *why* those failures occur with single-pass retrieval.
# 3. Implement an advanced retrieval strategy (query decomposition and/or graph
#    traversal) that addresses them.
# 4. Measure the improvement against your baseline using your 3.1 evaluation set.

# %% [markdown]
# ## Step 1 — Keep your capstone scenario
#
# Use the **same scenario** you chose in Checkpoint 1.1 and have built on since.
#
# | Scenario | Corpus | Natural relationships to exploit in a graph |
# |---|---|---|
# | **Research Paper Navigator** | ~150 research paper PDFs (`Labs/CapstoneDatasets/ResearchPapers/`) | citations, shared authors, shared topics/keywords, "published-before" |
# | **Wikipedia Retrieval Engine** | ~2,400 Wikipedia HTML articles (`Labs/CapstoneDatasets/Wikipedia/`) | hyperlinks between articles, shared categories, mentioned entities |
#
# Multistep decomposition shines on cross-document questions ("Compare X and Y,"
# "how did an idea evolve"); graph retrieval shines when the answer needs documents
# that are *related* to a hit but don't themselves match the query terms.

# %% [markdown]
# ## Setup (~5 min)
#
# 1. **Python 3.11 or 3.12**
# 2. `pip install langchain-openai langchain-core python-dotenv networkx`
# 3. Use the OpenRouter API key provided for this course. This checkpoint uses
#   the `openai/gpt-5.4-mini` model, with usage covered by course credits.
# 4. Create a `.env` file next to this script: `OPENROUTER_API_KEY=sk-or-v1-...`
#
# This script runs on a tiny built-in sample corpus, so you do **not** need your full
# dataset indexed to complete it. You *will* refer to your real 2.1 system and 3.1
# evaluation results when you write the report.

# %%
from __future__ import annotations

import warnings
warnings.filterwarnings("ignore")

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import networkx as nx
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

# %%
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
LLM_MODEL = "openai/gpt-5.4-mini"  # Latest small OpenAI model, fast; covered by course credits
TEMPERATURE = 0.2
LOG_PATH = Path.cwd() / "checkpoint_4_1_responses.log"

# === SET THIS to the scenario you chose in Checkpoint 1.1 ===
SCENARIO = "research_papers"   # "research_papers" or "wikipedia"

DECOMPOSE_SYSTEM = (
    "You are a query decomposition assistant for a document retrieval system. "
    "Break the user's question into 2-4 focused sub-queries that together cover "
    "everything needed to answer it. Each sub-query should target a distinct aspect. "
    'Return ONLY a JSON array of strings, e.g., ["sub-query 1", "sub-query 2"].'
)

ANSWER_SYSTEM = (
    "You are a helpful assistant. Answer the question using only the provided "
    "documents, and quote from them where you can. If the documents do not contain "
    "the answer, say so rather than guessing."
)


# %%
def check_api_key() -> str:
    load_dotenv()
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError(
            "OPENROUTER_API_KEY not set. Grab a free key at "
            "https://openrouter.ai/keys, put it in a .env file next to this "
            "script, and rerun."
        )
    return key


def make_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=LLM_MODEL,
        temperature=TEMPERATURE,
        api_key=check_api_key(),
        base_url=OPENROUTER_BASE_URL,
    )


def log_response(label: str, prompt: str, response: str) -> None:
    ts = datetime.now().isoformat(timespec="seconds")
    entry = (
        f"[{ts}]  {label}  SCENARIO={SCENARIO}  MODEL={LLM_MODEL}\n"
        f"PROMPT:   {prompt}\n"
        f"RESPONSE: {response}\n"
        f"{'-' * 72}\n"
    )
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(entry)


# %% [markdown]
# ## A tiny sample corpus (stands in for your real one)
#
# Six short "documents" with relationships so both techniques are demonstrable
# without indexing your full corpus. Each has an ID, text, a `topics` list, and
# `links` to related documents (i.e., think citations for papers, or hyperlinks for
# Wikipedia). Your real system would derive these from your actual data.

# %%
SAMPLE_DOCS = [
    {"id": "d1", "text": "Paper on retrieval-augmented generation: Grounding LLM answers in retrieved documents reduces hallucination.",
     "topics": ["RAG", "hallucination"], "links": ["d2", "d3"]},
    {"id": "d2", "text": "Study of hallucination in language models: Models fabricate specifics when they lack grounding.",
     "topics": ["hallucination"], "links": ["d1"]},
    {"id": "d3", "text": "Hybrid retrieval combines keyword and vector search to improve recall over either alone.",
     "topics": ["RAG", "retrieval"], "links": ["d1", "d4"]},
    {"id": "d4", "text": "Query decomposition breaks a complex question into sub-queries, improving multi-aspect retrieval.",
     "topics": ["retrieval", "decomposition"], "links": ["d3"]},
    {"id": "d5", "text": "Graph-based retrieval traverses relationships between documents to add related context.",
     "topics": ["retrieval", "graph"], "links": ["d4", "d6"]},
    {"id": "d6", "text": "Evaluation of RAG systems uses an LLM judge to score answers against grading notes.",
     "topics": ["evaluation", "RAG"], "links": ["d5"]},
]
DOC_BY_ID = {d["id"]: d for d in SAMPLE_DOCS}


def keyword_score(query: str, text: str) -> float:
    """A tiny, dependency-free relevance score: shared word count. This stands in for
    your real hybrid retriever, so the retrieval step needs no extra dependencies. The
    demo still calls the LLM, which requires an OpenRouter API key."""
    q = set(re.findall(r"[a-z0-9]+", query.lower()))
    t = set(re.findall(r"[a-z0-9]+", text.lower()))
    return float(len(q & t))


def baseline_retrieve(query: str, k: int = 3) -> list[tuple[str, float]]:
    """Single-pass retrieval: Score every doc once, take the top k. (id, score)."""
    scored = [(d["id"], keyword_score(query, d["text"])) for d in SAMPLE_DOCS]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [(i, s) for i, s in scored[:k] if s > 0]


# %% [markdown]
# ## Step 2 — Multistep retrieval (provided, adapted from Lab 4.1)
#
# `decompose_query` asks the LLM to split the question into sub-queries. For each
# sub-query, we retrieve the top documents and **sum** each document's score across
# the sub-queries. A document relevant to several parts of the question rises to the
# top. (In your real system, replace `baseline_retrieve` with your 2.1 retriever.)

# %%
def decompose_query(llm: ChatOpenAI, query: str) -> list[str]:
    messages = [SystemMessage(content=DECOMPOSE_SYSTEM), HumanMessage(content=query)]
    raw = llm.invoke(messages).content.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw[raw.find("["): raw.rfind("]") + 1] if "[" in raw else raw
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list) and all(isinstance(x, str) for x in parsed) and parsed:
            return parsed
    except (json.JSONDecodeError, ValueError):
        pass
    return [query]


def multistep_retrieve(llm: ChatOpenAI, query: str, k: int = 3) -> list[str]:
    sub_queries = decompose_query(llm, query)
    print(f"  decomposed into: {sub_queries}")
    score_map: dict[str, float] = {}
    for sq in sub_queries:
        for doc_id, score in baseline_retrieve(sq, 3 * k):
            score_map[doc_id] = score_map.get(doc_id, 0.0) + score
    ranked = sorted(score_map.items(), key=lambda kv: kv[1], reverse=True)
    return [doc_id for doc_id, _ in ranked[:k]]


# %% [markdown]
# ## Step 3 — Graph-based retrieval (provided, adapted from Lab 4.2)
#
# Build a graph whose nodes are documents and topics, with edges for "links to" and
# "relates to topic." Retrieval seeds with the baseline hits, then pulls in each
# seed's linked documents and topic-siblings as extra context — deduplicated.

# %%
def build_graph(docs: list[dict]) -> nx.DiGraph:
    G = nx.DiGraph()
    for d in docs:
        G.add_node(f"doc:{d['id']}", node_type="doc")
        for other in d["links"]:
            G.add_edge(f"doc:{d['id']}", f"doc:{other}", edge_type="links_to")
        for topic in d["topics"]:
            G.add_node(f"topic:{topic}", node_type="topic")
            G.add_edge(f"doc:{d['id']}", f"topic:{topic}", edge_type="relates_to")
    return G


def graph_retrieve(graph: nx.DiGraph, query: str, k: int = 3) -> dict[str, str]:
    """Return {doc_id: source_label}: baseline seeds plus their graph neighbors."""
    union: dict[str, str] = {}
    for doc_id, _ in baseline_retrieve(query, k):
        union[doc_id] = "seed"
    for seed in list(union):
        node = f"doc:{seed}"
        if not graph.has_node(node):
            continue
        for _, target, ed in graph.out_edges(node, data=True):
            if ed.get("edge_type") == "links_to":
                union.setdefault(target.removeprefix("doc:"), "linked")
            elif ed.get("edge_type") == "relates_to":
                for sib, _, ed2 in graph.in_edges(target, data=True):  # Source docs on this topic
                    if ed2.get("edge_type") == "relates_to":
                        union.setdefault(sib.removeprefix("doc:"), "topic")
    return union


# %% [markdown]
# ## Step 4 — Your advanced-retrieval plan (TODO)
#
# Design how you will apply these techniques to **your** capstone corpus. Return a
# dictionary with the keys below. This is the plan you will implement in your real system
# and describe in the report. Keep it concrete and specific to your scenario.

# %%
def my_advanced_plan() -> dict[str, Any]:
    """Return YOUR advanced-retrieval plan for your chosen scenario.

    TODO — your turn. Return a dictionary with these keys:
      - "technique":   "decomposition", "graph", or "both"
      - "node_types":  list[str]  — for graph: the kinds of nodes in your corpus
                       (e.g., ["paper", "author", "topic"] or ["article", "category"])
      - "edge_types":  list[str]  — the relationships you will surface
                       (e.g., ["cites", "same_author", "shares_topic"])
      - "test_queries": list[str] — 2-3 questions from your 3.1 evaluation set that
                       single-pass retrieval handled poorly and that should improve.
      - "rationale":   str — one or two sentences on why these choices fit your data.

    Delete the raise NotImplementedError line once your code works.
    """
    return {'technique': 'decomposition', 'node_types': [], 'edge_types': [], 'test_queries': ['Compare how SPARLING and The Sketching Approach to Program Synthesis use supervision or specification to guide learning or synthesis.', 'Which papers describe systems that complete missing parts of a program from examples or constraints?'], 'rationale': 'Q3 missed the named Sketching paper; Q4 retrieved insufficient evidence for concept-based discovery. Apply MIT decomposition and sum fusion to the unchanged BM25 baseline, keeping three final pages. No graph is implemented for the real corpus in this experiment.'}


# %% [markdown]
# ## Step 5 — Run baseline vs. advanced and capture the evidence
#
# This demonstration compares single-pass retrieval with the two advanced retrieval strategies 
# using the sample corpus and a representative query. It also logs the result. Read the
# retrieved sets: The advanced strategies should surface related documents that the
# baseline misses. Then run the same comparison in your real system for your report.

# %%
def answer_from_docs(llm: ChatOpenAI, query: str, doc_ids: list[str]) -> str:
    context = "\n\n".join(f"[{i}] {DOC_BY_ID[i]['text']}" for i in doc_ids if i in DOC_BY_ID)
    messages = [
        SystemMessage(content=ANSWER_SYSTEM),
        HumanMessage(content=f"Documents:\n{context}\n\nQuestion: {query}"),
    ]
    return llm.invoke(messages).content


def run_demo() -> None:
    llm = make_llm()
    graph = build_graph(SAMPLE_DOCS)
    query = "How does breaking a question into parts and following document links help retrieval?"

    print("=" * 72)
    print(f"Checkpoint 4.1 demo — scenario: {SCENARIO}\nQuery: {query}\n")

    base = [i for i, _ in baseline_retrieve(query, 3)]
    print(f"BASELINE (single-pass) retrieved: {base}")

    multi = multistep_retrieve(llm, query, 3)
    print(f"MULTI-STEP retrieved:             {multi}")

    g = graph_retrieve(graph, query, 3)
    print(f"GRAPH retrieved (with sources):   {g}")

    answer = answer_from_docs(llm, query, list(g.keys()))
    print(f"\nGraph-augmented answer:\n{answer}\n")
    log_response("GRAPH", query, answer)

    # Show your own plan was filled in.
    try:
        plan = my_advanced_plan()
        print("Your advanced-retrieval plan:")
        print(json.dumps(plan, indent=2))
    except NotImplementedError as e:
        print(f"[my_advanced_plan not done yet] {e}")

    print("=" * 72)
    print("Done. Now reproduce this comparison in YOUR real system (baseline vs "
          "advanced, matched document count) and use the numbers in your report.")


# Demo is selected explicitly by the command-line entry point below.

# %% [markdown]
# ## Step 6
#
# The checkpoint deliverable is your completed Capstone Checkpoint 4.1 worksheet, not
# code. Using evidence from your real system, cover:
#
# 1. **System overview** State your scenario and your 2.1 baseline retriever.
# 2. **Failure diagnosis** Describe the meaningful retrieval failure or limitation identified through
#    your Checkpoint 3.1 evaluation and explain why it occurs.
# 3. **Data redesign** Describe the node/edge schema you defined to expose relationships in
#    your corpus (citations/authors/topics, or links/categories/entities), and why you chose it. 
# 4. **Advanced retrieval implemented** Provide a query decomposition and/or graph traversal,
#    with code or log evidence. Label primary vs. context documents in the prompt.
# 5. **Comparative evaluation** Re-run your 3.1 evaluation on baseline vs advanced,
#    **comparing a similar number of retrieved documents**, and report before/after.
# 6. **Analysis & reflection** Discuss where it helped, where it hurt (redundant/over-broad
#    context), the cost/latency trade-off, and remaining limitations.
#

# %% Research Paper Navigator adaptation and reproducible comparison
# The sample demo above is retained. Real evaluation imports the unchanged 2.1
# baseline and uses the same 3.1 questions and RAGAS metrics. No graph is invented.
import argparse
import hashlib
import importlib.util
import time
import platform
from importlib.metadata import version

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BASELINE = REPO / 'capstone-project/capstone-checkpoint-2.1/capstone_checkpoint_2_1_baseline_retrieval_solution.py'
EVAL31 = REPO / 'capstone-project/capstone-checkpoint-3.1/MIT_Checkpoint_3_1_Evaluation'

def fingerprint(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def write_json(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write('\n')

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def check_inputs():
    config = read_json(EVAL31 / 'input/config.json')
    run_config = read_json(EVAL31 / 'results/mit_eval_01/run_config.json')
    if fingerprint(BASELINE) != config['baseline_sha256']:
        raise RuntimeError('Baseline code changed since 3.1')
    for filename, expected in run_config['input_hashes'].items():
        if fingerprint(EVAL31 / 'input' / filename) != expected:
            raise RuntimeError('3.1 input changed: ' + filename)
    if fingerprint(EVAL31 / 'evaluate_research_papers.py') != run_config['adapter_sha256']:
        raise RuntimeError('3.1 evaluator changed')
    if fingerprint(EVAL31 / 'reference/lab_3_1_evaluation_solution.py') != run_config['mit_solution_sha256']:
        raise RuntimeError('MIT evaluator changed')
    return config, run_config, read_json(EVAL31 / 'input/evidence.json')

class RecordedLLM:
    """Capture usage returned by the API; no estimated dollar costs are invented."""
    def __init__(self, client):
        self.client = client
        self.calls = []
    def invoke(self, messages):
        start = time.perf_counter()
        result = self.client.invoke(messages)
        self.calls.append({'seconds': time.perf_counter()-start,
                           'usage': getattr(result, 'usage_metadata', None)})
        return result

def retrieve_decomposed(base, client, question, documents, index):
    start = time.perf_counter()
    raw = client.invoke([SystemMessage(content=DECOMPOSE_SYSTEM), HumanMessage(content=question)]).content
    subqueries = []
    fallback = None
    try:
        clean = raw.strip()
        if clean.startswith('```'):
            clean = clean[clean.find('['):clean.rfind(']')+1]
        parsed = json.loads(clean)
        if not isinstance(parsed, list) or not 1 <= len(parsed) <= 4:
            raise ValueError('Expected 1-4 queries')
        for item in parsed:
            if not isinstance(item, str) or not item.strip():
                raise ValueError('Empty or non-string query')
            if item.strip() not in subqueries:
                subqueries.append(item.strip())
    except (ValueError, TypeError, AttributeError) as exc:
        subqueries = [question]
        fallback = str(exc)
    decomposition_seconds = time.perf_counter()-start
    started_search = time.perf_counter()
    scores, content, candidates = {}, {}, []
    for sq in subqueries:
        hits = base.retrieve(sq, documents, index, 9)
        candidates.append({'subquery': sq, 'hits': [{'id': d['id'], 'score': s} for d,s in hits]})
        for doc, score in hits:
            content[doc['id']] = doc
            scores[doc['id']] = scores.get(doc['id'], 0.0) + score
    chosen = sorted(scores, key=lambda key: scores[key], reverse=True)[:3]
    return [(content[key], scores[key]) for key in chosen], {
        'raw_decomposition': raw, 'subqueries': subqueries, 'fallback': fallback,
        'candidates': candidates, 'decomposition_seconds': decomposition_seconds,
        'search_and_fusion_seconds': time.perf_counter()-started_search,
        'selection': 'Sum BM25 scores over subqueries, deduplicate by page ID, top three pages',
        'graph_context_documents': [],
    }

def compare(args):
    capture_config, old_run, evidence = check_inputs()
    corpus = Path(args.corpus).expanduser().resolve()
    actual = {p.name:fingerprint(p) for p in sorted(corpus.glob('*.pdf'))}
    expected = {item['file']:item['sha256'] for item in capture_config['corpus']}
    if actual != expected:
        raise RuntimeError('PDF corpus does not match the 3.1 snapshot; no API calls made')
    out = HERE / args.out
    if out.exists():
        raise RuntimeError('Output already exists; preserve it and choose another --out')
    base = load_module('baseline21', BASELINE)
    if (base.LLM_MODEL != capture_config['model'] or base.TEMPERATURE != capture_config['temperature']
        or base.ANSWER_SYSTEM != capture_config['answer_prompt']):
        raise RuntimeError('Answer configuration differs from 3.1')
    extraction_start = time.perf_counter()
    documents = base.load_pdf_corpus(corpus)
    if len(documents) != capture_config['readable_pages']:
        raise RuntimeError('Page count differs from 3.1; inspect extraction before comparison')
    index = base.build_bm25(documents)
    extraction_seconds = time.perf_counter()-extraction_start
    # Validate every original retrieval before incurring inference charges.
    baseline_hits = {}
    for case in evidence:
        hits = base.retrieve(case['question'], documents, index, 3)
        if [(d['id'], d['text']) for d,s in hits] != [(h['id'],h['text']) for h in case['retrieved']]:
            raise RuntimeError('Baseline retrieval differs from 3.1: ' + case['id'])
        baseline_hits[case['id']] = hits
    print('VERIFIED: Corpus, page count, and all original top-three passages match 3.1.', flush=True)
    evaluator = load_module('adapter31', EVAL31 / 'evaluate_research_papers.py')
    mit = load_module('mit31', EVAL31 / 'reference/lab_3_1_evaluation_solution.py')
    mit.require_api_key()
    judge = mit.make_judge()
    refined = mit.DiscreteMetric(name='grounded_correctness', prompt=evaluator.REFINED_PROMPT, allowed_values=['pass','fail'])
    llm = RecordedLLM(base.make_llm())
    out.mkdir(parents=True)
    write_json(out/'run_config.json', {
        'timestamp': datetime.now().astimezone().isoformat(), 'scenario': SCENARIO,
        'python': platform.python_version(),
        'packages': {n:version(n) for n in ['pypdf','rank-bm25','langchain-openai','ragas','openai']},
        'solution_sha256':fingerprint(__file__), 'baseline_sha256':fingerprint(BASELINE),
        'prior_run_config_sha256':fingerprint(EVAL31/'results/mit_eval_01/run_config.json'),
        'answer_model':base.LLM_MODEL,'temperature':base.TEMPERATURE,'judge_model':mit.JUDGE_MODEL,
        'endpoint':mit.OPENROUTER_BASE_URL,'answer_prompt':base.ANSWER_SYSTEM,
        'decomposition_prompt':DECOMPOSE_SYSTEM,'original_metric_prompt':old_run['original_metric_prompt'],
        'refined_metric_prompt':evaluator.REFINED_PROMPT,'plan':my_advanced_plan(),
        'matched_page_limit':3,'candidate_pages_per_subquery':9,
        'corpus':capture_config['corpus'],'readable_pages':len(documents),
        'extraction_and_index_seconds':extraction_seconds,
        'limitations':['One run; four selected questions; no independent held-out set.',
                      'Same page limit, not identical token count.',
                      'Sum fusion may favor common or repeated aspects; duplicate paper versions remain.',
                      '3.1 judge citation miss and abstention ambiguity remain.',
                      'API dollar cost not measured; usage is recorded when returned.']})
    records = []
    for case in evidence:
        for arm in ['baseline','decomposition']:
            calls_start = len(llm.calls)
            start = time.perf_counter()
            if arm == 'baseline':
                hits = base.retrieve(case['question'], documents, index, 3)
                trace = {'subqueries':[case['question']], 'graph_context_documents':[]}
            else:
                hits, trace = retrieve_decomposed(base,llm,case['question'],documents,index)
            retrieval_seconds = time.perf_counter()-start
            answer_start = time.perf_counter()
            response = base.answer(llm,case['question'],hits)
            answer_seconds = time.perf_counter()-answer_start
            row = {'id':case['id'],'arm':arm,'question':case['question'],'grading_notes':case['grading_notes'],
                   'response':response,'retrieved':[dict(d, score=s, role='primary') for d,s in hits],
                   'trace':trace,'retrieval_seconds':retrieval_seconds,'answer_seconds':answer_seconds,
                   'pipeline_seconds':retrieval_seconds+answer_seconds,'llm_calls':llm.calls[calls_start:]}
            write_json(out/f"{case['id']}_{arm}_capture.json",row)
            context = '\n\n---\n\n'.join(f"[{d['id']}]\n{d['text']}" for d,s in hits)
            score = mit.correctness_metric.score(llm=judge,response=response,grading_notes=case['grading_notes'])
            stronger = refined.score(llm=judge,question=case['question'],response=response,
                                    grading_notes=case['grading_notes'],retrieved_context=context)
            if score.value not in ['pass','fail'] or stronger.value not in ['pass','fail']:
                raise RuntimeError('Unexpected judge value; partial capture retained')
            row.update(original_correctness=score.value,grounded_correctness=stronger.value)
            write_json(out/f"{case['id']}_{arm}_result.json",row)
            records.append(row)
            print(f"{case['id']} {arm}: original={score.value}; refined={stronger.value}; pages={len(hits)}",flush=True)
    write_json(out/'comparison_results.json',records)
    summaries = {}
    for arm in ['baseline','decomposition']:
        rows = [r for r in records if r['arm']==arm]
        summaries[arm] = {field:{'passed':sum(r[field]=='pass' for r in rows),'total':len(rows)}
                         for field in ['original_correctness','grounded_correctness']}
        summaries[arm]['mean_pipeline_seconds'] = sum(r['pipeline_seconds'] for r in rows)/len(rows)
        summaries[arm]['application_llm_calls'] = sum(len(r['llm_calls']) for r in rows)
    summaries['interpretation'] = 'Fresh paired comparison; retain historical 3.1 separately. Judge passes are not source recall. Timings exclude extraction and judging.'
    write_json(out/'comparison_summary.json',summaries)
    print(json.dumps(summaries,indent=2))
    print('COMPLETE:',out.resolve())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MIT Checkpoint 4.1: demo or matched research-paper comparison')
    parser.add_argument('mode',choices=['check','demo','compare'])
    parser.add_argument('--corpus',help='Original research-paper PDF directory')
    parser.add_argument('--out',default='runs/comparison_01')
    args = parser.parse_args()
    if args.mode == 'check':
        check_inputs()
        print('VERIFIED: 2.1 baseline and 3.1 evaluator/input hashes match. No API calls made.')
    elif args.mode == 'demo':
        run_demo()
    else:
        if not args.corpus:parser.error('--corpus is required for compare')
        compare(args)
