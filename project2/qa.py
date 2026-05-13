"""
qa.py — Ask questions against the wiki knowledge base.

Usage:
    python qa.py                        # interactive mode
    python qa.py "How does batch matching work?"

Two modes:
  - If ANTHROPIC_API_KEY is set: sends wiki context + question to Claude for a rich answer.
  - Otherwise: falls back to keyword search across wiki files (shows relevant excerpts).
"""

import os
import sys
import glob
import re

WIKI_DIR = "wiki"

QA_PROMPT = """\
You are an expert assistant on food delivery dispatch algorithms.
Answer the user's question using ONLY the information in the wiki articles below.
Be concise and precise. If the wiki does not contain enough information to answer,
say so explicitly.

=== WIKI ARTICLES ===
{wiki_context}
=== END OF WIKI ===

Question: {question}

Answer:"""


def load_wiki() -> dict[str, str]:
    """Load all wiki markdown files into a dict {filepath: content}."""
    files = glob.glob(os.path.join(WIKI_DIR, "**", "*.md"), recursive=True)
    wiki = {}
    for f in sorted(files):
        with open(f, encoding="utf-8") as fh:
            wiki[f] = fh.read()
    return wiki


def keyword_search(wiki: dict[str, str], question: str, top_k: int = 3) -> list[tuple[str, str]]:
    """Return the top_k most relevant wiki files based on keyword overlap."""
    words = set(re.sub(r"[^\w\s]", "", question.lower()).split())
    scores = []
    for path, content in wiki.items():
        content_lower = content.lower()
        score = sum(1 for w in words if w in content_lower)
        scores.append((score, path, content))
    scores.sort(reverse=True)
    return [(path, content) for _, path, content in scores[:top_k]]


def answer_with_llm(wiki: dict[str, str], question: str) -> str:
    """Use Claude API to answer the question using wiki context."""
    import anthropic

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    client = anthropic.Anthropic(api_key=api_key)

    # Select the most relevant wiki pages (to stay within context limits)
    relevant = keyword_search(wiki, question, top_k=4)
    wiki_context = "\n\n---\n\n".join(
        f"[{os.path.basename(path)}]\n{content}" for path, content in relevant
    )

    prompt = QA_PROMPT.format(wiki_context=wiki_context, question=question)

    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def answer_with_search(wiki: dict[str, str], question: str) -> str:
    """Keyword-based fallback: return relevant excerpts from the wiki."""
    relevant = keyword_search(wiki, question, top_k=2)
    if not relevant:
        return "No relevant wiki articles found."

    output_lines = [f"[Keyword search — set ANTHROPIC_API_KEY for LLM answers]\n"]
    for path, content in relevant:
        output_lines.append(f">>> {os.path.relpath(path, WIKI_DIR)}")
        # Show first 30 lines of the article
        snippet = "\n".join(content.splitlines()[:30])
        output_lines.append(snippet)
        output_lines.append("")
    return "\n".join(output_lines)


def answer(question: str) -> str:
    wiki = load_wiki()
    if not wiki:
        return "Wiki is empty. Run ingest.py first."
    if os.environ.get("ANTHROPIC_API_KEY"):
        return answer_with_llm(wiki, question)
    else:
        return answer_with_search(wiki, question)


def interactive_mode():
    print("Food Delivery Dispatch Wiki Q&A")
    print("Type 'quit' to exit.\n")
    while True:
        try:
            question = input("Q: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if question.lower() in ("quit", "exit", "q"):
            break
        if not question:
            continue
        print("\nA:", answer(question), "\n")


def main():
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        print(answer(question))
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
