from datasets import load_dataset
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def dump_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} rows -> {path}")


def download_scifact():
    out_dir = os.path.join(DATA_DIR, "scifact")
    os.makedirs(out_dir, exist_ok=True)

    corpus = load_dataset("BeIR/scifact", "corpus")["corpus"]
    queries = load_dataset("BeIR/scifact", "queries")["queries"]
    qrels = load_dataset("BeIR/scifact-qrels")["test"]

    dump_jsonl(
        os.path.join(out_dir, "corpus.jsonl"),
        [{"doc_id": r["_id"], "title": r["title"], "text": r["text"]} for r in corpus],
    )
    dump_jsonl(
        os.path.join(out_dir, "queries.jsonl"),
        [{"query_id": r["_id"], "text": r["text"]} for r in queries],
    )
    dump_jsonl(
        os.path.join(out_dir, "qrels.jsonl"),
        [{"query_id": str(r["query-id"]), "doc_id": str(r["corpus-id"]), "relevance": r["score"]} for r in qrels],
    )


def download_squad(n=500):
    out_dir = os.path.join(DATA_DIR, "squad")
    os.makedirs(out_dir, exist_ok=True)

    ds = load_dataset("rajpurkar/squad_v2", split=f"validation[:{n}]")
    rows = []
    for r in ds:
        if not r["answers"]["text"]:
            continue
        rows.append(
            {
                "question": r["question"],
                "context": r["context"],
                "answer": r["answers"]["text"][0],
                "title": r["title"],
            }
        )
    dump_jsonl(os.path.join(out_dir, "eval.jsonl"), rows)


def download_hotpotqa(n=300):
    out_dir = os.path.join(DATA_DIR, "hotpotqa")
    os.makedirs(out_dir, exist_ok=True)

    ds = load_dataset("hotpotqa/hotpot_qa", "distractor", split=f"validation[:{n}]", trust_remote_code=True)
    rows = []
    for r in ds:
        supporting_titles = set(r["supporting_facts"]["title"])
        context_docs = [
            {"title": t, "sentences": s}
            for t, s in zip(r["context"]["title"], r["context"]["sentences"])
        ]
        rows.append(
            {
                "question": r["question"],
                "answer": r["answer"],
                "type": r["type"],
                "level": r["level"],
                "supporting_titles": list(supporting_titles),
                "context_docs": context_docs,
            }
        )
    dump_jsonl(os.path.join(out_dir, "eval.jsonl"), rows)


if __name__ == "__main__":
    download_scifact()
    download_squad()
    download_hotpotqa()
