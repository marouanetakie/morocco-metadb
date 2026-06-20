import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

NCBI_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
NCBI_API_KEY = os.getenv("NCBI_API_KEY", "")


def _ncbi_params(extra: dict) -> dict:
    p = {"retmode": "json"}
    if NCBI_API_KEY:
        p["api_key"] = NCBI_API_KEY
    p.update(extra)
    return p


def search_pubmed(query: str, max_results: int = 10) -> list:
    r = requests.get(
        f"{NCBI_BASE}/esearch.fcgi",
        params=_ncbi_params({"db": "pubmed", "term": query, "retmax": max_results}),
        timeout=15,
    )
    r.raise_for_status()
    ids = r.json()["esearchresult"]["idlist"]
    if not ids:
        return []

    r2 = requests.get(
        f"{NCBI_BASE}/esummary.fcgi",
        params=_ncbi_params({"db": "pubmed", "id": ",".join(ids)}),
        timeout=15,
    )
    r2.raise_for_status()
    result = r2.json()["result"]

    articles = []
    for pmid in ids:
        if pmid not in result:
            continue
        a = result[pmid]
        articles.append({
            "pmid":    pmid,
            "title":   a.get("title", ""),
            "authors": ", ".join(x.get("name", "") for x in a.get("authors", [])),
            "journal": a.get("fulljournalname", ""),
            "year":    a.get("pubdate", "")[:4],
            "doi":     next(
                (x["value"] for x in a.get("articleids", []) if x["idtype"] == "doi"),
                None,
            ),
        })
    return articles


def search_for_plant(plant_name: str, max_results: int = 10) -> list:
    query = (
        f'"{plant_name}"[Title/Abstract] AND '
        "(phytochemical OR biological activity OR ethnobotany OR antioxidant)"
    )
    return search_pubmed(query, max_results)


def search_for_compound(compound_name: str, plant_name: str = None,
                        max_results: int = 10) -> list:
    query = f'"{compound_name}"[Title/Abstract]'
    if plant_name:
        query += f' AND "{plant_name}"[Title/Abstract]'
    return search_pubmed(query, max_results)


def summarize_with_claude(articles: list, question: str) -> str:
    try:
        import anthropic
    except ImportError:
        return "anthropic package not installed — run: pip install anthropic"

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return "ANTHROPIC_API_KEY not set in .env"

    client = anthropic.Anthropic(api_key=api_key)
    context = json.dumps(articles, indent=2, ensure_ascii=False)
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": (
                f"Based on these PubMed articles:\n{context}\n\n"
                f"Answer concisely: {question}"
            ),
        }],
    )
    return msg.content[0].text


if __name__ == "__main__":
    print("Searching PubMed for Erodium moschatum...")
    results = search_for_plant("Erodium moschatum", max_results=5)
    for a in results:
        print(f"[{a['year']}] {a['title'][:80]}... — {a['journal']}")
    print(f"\nFound {len(results)} articles.")
