r"""Capstone Checkpoint 2.1 — BM25 retrieval over the research-paper corpus.
Jupytext-style cell markers (# %% / # %% [markdown]) — runnable as a
plain script AND openable as cells in VS Code / PyCharm / Jupytext.
"""

# %% [markdown]
# # Capstone Checkpoint 2.1 — Retrieval Strategy Design and Baseline Implementation
# **MO-LLM Module 2 / Required Capstone Checkpoint (120 minutes)**
#
# ## What this checkpoint is
#
# In Checkpoint 1.1, you showed that a plain LLM can't reliably answer questions about
# your corpus. Now, you will **add retrieval**: Design a retrieval strategy for your scenario
# and build a **baseline retrieval system** that finds the most relevant documents for
# a query, so the model can ground its answers in them.
#
# This mirrors the Module 2 labs — keyword (BM25), vector (semantic), and hybrid
# retrieval — applied to your own capstone corpus. The graded deliverable is the completed 
# Capstone Checkpoint 2.1 worksheet, which includes your written responses and evidence of your 
# retrieval system implementation and testing. This script provides a small working example of 
# baseline retrieval. Use it to understand the retrieval workflow, then adapt the code to implement 
# and test a baseline retriever using your selected capstone dataset.
#
# **Learning outcomes (Module 2):**
# 1. Design a retrieval strategy appropriate for a given dataset and query type.
# 2. Implement and test a baseline retrieval system using structured and/or semantic
#    approaches.

# %% [markdown]
# ## Step 1 — Keep your capstone scenario
#
# Use the **same scenario** you chose in Checkpoint 1.1.
#
# | Scenario | Corpus | Retrieval considerations |
# |---|---|---|
# | **Research Paper Navigator** | ~150 research-paper PDFs (`Labs/CapstoneDatasets/ResearchPapers/`) | long documents; you'll likely chunk them; questions often name a specific paper or compare papers. |
# | **Wikipedia Retrieval Engine** | ~2,400 Wikipedia HTML articles (`Labs/CapstoneDatasets/Wikipedia/`) | many short-to-medium articles; questions name a figure/place or span several articles. |
#
# A good baseline is keyword (BM25), semantic (embeddings + vector search), or a
# hybrid of both — exactly what you built in Labs 1.2–2.2.

# %% [markdown]
# ## Setup (~5 min)
#
# 1. **Python 3.11 or 3.12**
# 2. `pip install langchain-openai langchain-core python-dotenv`
# 3. Use the OpenRouter API key provided for this program. This checkpoint uses
#  the `openai/gpt-5.4-mini` model, with usage covered by the course credits. (this uses the paid gpt-5.4-mini chat model — covered by your course credits — and a keyword retriever, no embeddings).
# 4. Create a `.env` file next to this script: `OPENROUTER_API_KEY=sk-or-v1-...`
#
# This runs on a tiny built-in sample corpus, so you do not need to prepare your own
# dataset. It still requires an OpenRouter API key to run the LLM (it is not offline or
# free of API calls). Your real baseline (over your full corpus) is what you describe in
# the writeup.

# %%
from __future__ import annotations

import warnings
warnings.filterwarnings("ignore")

import os
import re
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pypdf import PdfReader
from rank_bm25 import BM25Okapi

# %%
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
LLM_MODEL = "openai/gpt-5.4-mini"  # latest small OpenAI model, fast; covered by course credits
TEMPERATURE = 0.2
TOP_K = 3
LOG_PATH = Path.cwd() / "checkpoint_2_1_retrieval.log"

# === SET THIS to the scenario you chose in Checkpoint 1.1 ===
SCENARIO = "research_papers"   # "research_papers" or "wikipedia"

ANSWER_SYSTEM = (
    "You are a helpful assistant. Answer the question using ONLY the provided "
    "documents, and quote from them where you can. If the documents do not contain "
    "the answer, say so rather than guessing."
)


# %%
def check_api_key() -> str:
    load_dotenv()
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. Use the OpenRouter API key "
            "provided for this course, put it in a .env file next to this "
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


def log(label: str, text: str) -> None:
    ts = datetime.now().isoformat(timespec="seconds")
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(f"[{ts}] {label}\n{text}\n{'-' * 72}\n")


# %% [markdown]
# ## Load the real research-paper corpus
#
# Each PDF page becomes one retrievable document. Page-level chunks are simple,
# preserve useful provenance, and avoid sending an entire paper to the LLM.


# %%
def load_pdf_corpus(pdf_dir: Path) -> list[dict[str, str]]:
    """Extract text from every readable PDF page in the selected corpus."""
    if not pdf_dir.is_dir():
        raise FileNotFoundError(f"Research-paper folder not found: {pdf_dir}")

    pdf_paths = sorted(pdf_dir.glob("*.pdf"))
    if not pdf_paths:
        raise FileNotFoundError(f"No PDF files found in: {pdf_dir}")

    documents: list[dict[str, str]] = []
    skipped_files = 0

    print(f"Reading {len(pdf_paths)} research papers from:\n  {pdf_dir}")
    for paper_number, pdf_path in enumerate(pdf_paths, 1):
        try:
            reader = PdfReader(pdf_path)
            for page_number, page in enumerate(reader.pages, 1):
                text = (page.extract_text() or "").strip()
                if len(text) < 80:
                    continue

                source = f"{pdf_path.name}, page {page_number}"
                documents.append(
                    {
                        "id": source,
                        "source": pdf_path.name,
                        "page": str(page_number),
                        "text": text,
                    }
                )
        except Exception as exc:
            skipped_files += 1
            print(f"Warning: skipped {pdf_path.name}: {exc}")

        if paper_number % 25 == 0 or paper_number == len(pdf_paths):
            print(f"  processed {paper_number}/{len(pdf_paths)} papers")

    if not documents:
        raise RuntimeError("No readable PDF pages were extracted.")

    print(
        f"Built corpus with {len(documents)} readable pages "
        f"({skipped_files} unreadable papers skipped).\n"
    )
    return documents


# %% [markdown]
# ## Step 2 — BM25 keyword baseline
#
# BM25 rewards informative query terms while controlling for document length and
# repeated words. It is a strong, explainable baseline for paper titles, authors,
# method names, exact terminology, and numeric references.

# %%
def _tokens(text: str) -> list[str]:
    """Lowercase and split text into searchable word/number tokens."""
    return re.findall(r"[a-z0-9]+", text.lower())


def build_bm25(documents: list[dict[str, str]]) -> BM25Okapi:
    """Build the BM25 index once over page text plus source filename."""
    tokenized_pages = [
        _tokens(f"{document['source']} {document['text']}")
        for document in documents
    ]
    return BM25Okapi(tokenized_pages)


def retrieve(
    query: str,
    documents: list[dict[str, str]],
    index: BM25Okapi,
    k: int = TOP_K,
) -> list[tuple[dict[str, str], float]]:
    """Rank corpus pages by BM25 score and return the top positive matches."""
    scores = index.get_scores(_tokens(query))
    ranked_indexes = sorted(
        range(len(scores)), key=lambda item: scores[item], reverse=True
    )
    return [
        (documents[item], float(scores[item]))
        for item in ranked_indexes[:k]
        if scores[item] > 0
    ]


def answer(
    llm: ChatOpenAI,
    query: str,
    hits: list[tuple[dict[str, str], float]],
) -> str:
    context = "\n\n".join(
        f"[{document['id']}]\n{document['text']}"
        for document, _ in hits
    )
    messages = [
        SystemMessage(content=ANSWER_SYSTEM),
        HumanMessage(content=f"Documents:\n{context}\n\nQuestion: {query}"),
    ]
    return llm.invoke(messages).content


# %% [markdown]
# ## Step 3 — Your representative queries (TODO)
#
# Submission item #2 asks for **3-5 representative queries** for your scenario and the
# results your system retrieves for each. Write those queries here. Some good ones include questions that:
#
# - Are answerable from **one** document (tests precision),
# - Need **several** documents (tests recall / aggregation),
# - Have wording that **differs** from the document's wording (i.e., tests whether
#   keyword vs. semantic retrieval matters for your corpus)
#
# Return a list of 3-5 query strings.

# %%
def my_representative_queries() -> list[str]:
    """Return 3-5 representative queries for YOUR chosen scenario.

    These queries test exact terminology, cross-paper comparison, and paraphrased
    conceptual retrieval.
    """
    return [
        (
            "According to SPARLING, what accuracy did the authors report for "
            "localizing intermediate states on synthetic domains?"
        ),
        (
            "How does The Sketching Approach to Program Synthesis describe the "
            "role of holes and specifications?"
        ),
        (
            "Compare how SPARLING and The Sketching Approach to Program Synthesis "
            "use supervision or specification to guide learning or synthesis."
        ),
        (
            "Which papers describe systems that complete missing parts of a "
            "program from examples or constraints?"
        ),
    ]


# %% [markdown]
# ## Step 4 — Run the baseline and capture the evidence
#
# This runs each query through the baseline retriever and the LLM, printing the
# retrieved document ids/scores and the grounded answer, and logging everything to
# `checkpoint_2_1_retrieval.log`. The retrieved documents from the output are the rest of the evidence for
# submission item #2.

# %%
def run() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python capstone_checkpoint_2_1_baseline_retrieval_solution.py "
            "<ResearchPapers_folder>"
        )

    pdf_dir = Path(sys.argv[1]).expanduser().resolve()
    documents = load_pdf_corpus(pdf_dir)
    index = build_bm25(documents)
    llm = make_llm()
    queries = my_representative_queries()
    print(f"Checkpoint 2.1 — BM25 retrieval  |  scenario: {SCENARIO}\n")
    for i, query in enumerate(queries, 1):
        hits = retrieve(query, documents, index, TOP_K)
        print("=" * 72)
        print(f"QUERY {i}: {query}")
        if not hits:
            print("  (nothing matched — note this in your writeup)")
            continue

        print("  retrieved:")
        for rank, (document, score) in enumerate(hits, 1):
            print(f"    {rank}. {document['id']} | BM25={score:.3f}")

        ans = answer(llm, query, hits)
        print(f"  answer: {ans}\n")
        evidence = "\n".join(
            f"{rank}. {document['id']} | BM25={score:.3f}"
            for rank, (document, score) in enumerate(hits, 1)
        )
        log(f"QUERY {i}: {query}", f"retrieved:\n{evidence}\n\nanswer={ans}")
    print("=" * 72)
    print("Done. Use the retrieved document results above as evidence in your writeup, and "
          "describe your REAL baseline (over your full corpus) in the submission.")


if __name__ == "__main__":
    run()

# %% [markdown]
# ## Step 5 — Your written submission (the graded deliverable)
#
# Use your completed retrieval implementation and test results to complete the Capstone Checkpoint 2.1
# worksheet. In the worksheet, you will document your retrieval approach, provide evidence that your 
# system is functioning, include 3–5 representative queries and retrieved results, and reflect on where
# your approach performs well and where it struggles.  
 
# Save your completed Python file in the appropriate checkpoint folder in your GitHub repository. 
# Upload the completed worksheet only to the learning platform as your graded submission.
