"""
ingest.py — Compile raw source documents into a linked wiki.

Usage:
    python ingest.py                    # process all files in raw/
    python ingest.py raw/some_file.md   # process a single file

How it works:
1. Reads every .md / .txt file in raw/
2. Sends each file to an LLM with a prompt that asks it to:
   - Write a clean wiki article summarising the source
   - Identify key concepts and link them with [[concept]] syntax
   - Suggest related articles
3. Saves the result into wiki/<category>/<title>.md
4. Updates wiki/INDEX.md with a one-line summary of every article

If ANTHROPIC_API_KEY is not set, the script prints what it *would* do
(dry-run mode) so you can see the pipeline without spending tokens.
"""

import os
import sys
import glob
import anthropic

WIKI_DIR = "wiki"
RAW_DIR = "raw"
INDEX_PATH = os.path.join(WIKI_DIR, "INDEX.md")

INGEST_PROMPT = """\
You are a knowledge-base compiler. I will give you a raw source document about
food delivery dispatch algorithms. Your job is to:

1. Write a clean, well-structured wiki article (300-500 words) summarising the
   key ideas. Use markdown headings (## and ###).
2. Whenever you mention a concept that deserves its own article, wrap it in
   double brackets: [[Bipartite Matching]], [[ETA Prediction]], etc.
3. At the end of the article, add a section:
   ## See Also
   - [[RelatedConcept1]]
   - [[RelatedConcept2]]
4. Add a one-line "summary:" tag at the very top like:
   summary: <one sentence describing this article>

Raw source:
---
{source}
---

Write only the wiki article. Do not include any meta-commentary.
"""


def load_raw_sources(path=RAW_DIR):
    files = glob.glob(os.path.join(path, "*.md")) + glob.glob(os.path.join(path, "*.txt"))
    sources = {}
    for f in sorted(files):
        with open(f, encoding="utf-8") as fh:
            sources[f] = fh.read()
    return sources


def choose_wiki_path(filename: str, content: str) -> str:
    """Decide which subdirectory to place the article in based on filename."""
    name = os.path.splitext(os.path.basename(filename))[0]
    if any(k in name for k in ["algorithm", "match", "routing", "batch"]):
        subdir = "algorithms"
    elif any(k in name for k in ["ml", "rl", "learning"]):
        subdir = "concepts"
    elif any(k in name for k in ["company", "uber", "doordash", "meituan"]):
        subdir = "companies"
    else:
        subdir = "concepts"
    return os.path.join(WIKI_DIR, subdir, name + ".md")


def call_llm(prompt: str) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[dry-run] ANTHROPIC_API_KEY not set — skipping LLM call.")
        print("[dry-run] Prompt preview (first 200 chars):")
        print(prompt[:200])
        return ""

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def update_index(title: str, summary: str, wiki_path: str):
    rel_path = os.path.relpath(wiki_path, WIKI_DIR)
    entry = f"- [{title}]({rel_path}) — {summary}\n"
    with open(INDEX_PATH, "a", encoding="utf-8") as f:
        f.write(entry)


def ingest_file(filepath: str, dry_run: bool = False):
    with open(filepath, encoding="utf-8") as f:
        source = f.read()

    prompt = INGEST_PROMPT.format(source=source)
    wiki_content = call_llm(prompt)

    if not wiki_content:
        return  # dry-run or error

    wiki_path = choose_wiki_path(filepath, wiki_content)
    os.makedirs(os.path.dirname(wiki_path), exist_ok=True)
    with open(wiki_path, "w", encoding="utf-8") as f:
        f.write(wiki_content)
    print(f"  Wrote: {wiki_path}")

    # Extract summary line for index
    summary = ""
    for line in wiki_content.splitlines():
        if line.startswith("summary:"):
            summary = line.replace("summary:", "").strip()
            break

    title = os.path.splitext(os.path.basename(filepath))[0].replace("_", " ").title()
    update_index(title, summary, wiki_path)


def main():
    os.makedirs(WIKI_DIR, exist_ok=True)
    # Initialise index
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write("# Wiki Index\n\n")

    targets = sys.argv[1:] if len(sys.argv) > 1 else list(load_raw_sources().keys())
    for filepath in targets:
        print(f"Ingesting: {filepath}")
        ingest_file(filepath)

    print("\nDone. Index written to", INDEX_PATH)


if __name__ == "__main__":
    main()
