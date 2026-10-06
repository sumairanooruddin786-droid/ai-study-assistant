"""Core RAG pipeline: extract -> chunk -> embed -> store (ChromaDB) -> retrieve -> generate (LLM)."""
import os
import re
import time
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = Path(os.getenv("CHROMA_DIR", BASE_DIR / "chroma_db"))
SAMPLE_DIR = BASE_DIR / "sample_pdfs"
COLLECTION_NAME = "python_notes"

CHUNK_SIZE = 600      # characters per chunk
CHUNK_OVERLAP = 100   # characters shared between neighbouring chunks
EMBEDDING_MODEL = "all-MiniLM-L6-v2 (ONNX, 384 dimensions)"

_client = None
_ef = None


def get_collection():
    """Open (or create) the persistent ChromaDB collection."""
    global _client, _ef
    if _client is None:
        DB_DIR.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(DB_DIR))
    if _ef is None:
        _ef = embedding_functions.DefaultEmbeddingFunction()
    return _client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=_ef,
        metadata={"hnsw:space": "cosine"},
    )


# ---------- 1. Extract ----------
def extract_pages(data) -> list[tuple[int, str]]:
    """Return [(page_number, text)] for a PDF given as a path or file-like object."""
    reader = PdfReader(data)
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append((i, text))
    return pages


# ---------- 2. Chunk ----------
def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks, preferring paragraph / sentence boundaries."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text:
        return []
    if len(text) <= size:
        return [text]
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            window = text[start:end]
            cut = max(window.rfind("\n\n"), window.rfind(". "), window.rfind("\n"))
            if cut > size * 0.5:
                end = start + cut + 1
        piece = text[start:end].strip()
        if len(piece) > 40:
            chunks.append(piece)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def pretty_name(filename: str) -> str:
    stem = Path(filename).stem
    stem = re.sub(r"[_\-]+", " ", stem)
    return stem.strip().title()


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


# ---------- 3 + 4. Embed & store ----------
def ingest_pdf(filename: str, data) -> dict:
    """Extract, chunk, embed and store one PDF. Returns stats for the UI."""
    t0 = time.time()
    col = get_collection()
    pages = extract_pages(data)
    if not pages:
        raise ValueError(f"No readable text found in '{filename}' (scanned PDF?).")

    # Re-uploading the same file replaces its old chunks
    col.delete(where={"source": filename})

    ids, docs, metas = [], [], []
    slug = slugify(Path(filename).stem)
    total_chars = 0
    for page_no, text in pages:
        total_chars += len(text)
        for idx, chunk in enumerate(chunk_text(text)):
            ids.append(f"{slug}-p{page_no}-c{idx}")
            docs.append(chunk)
            metas.append({"source": filename, "chapter": pretty_name(filename),
                          "page": page_no, "chunk": idx, "chars": len(chunk)})

    t_embed = time.time()
    for i in range(0, len(ids), 64):  # Chroma embeds the documents automatically
        col.add(ids=ids[i:i + 64], documents=docs[i:i + 64], metadatas=metas[i:i + 64])
    embed_secs = time.time() - t_embed

    preview = None
    if ids:
        got = col.get(ids=[ids[0]], include=["embeddings"])
        vec = got["embeddings"][0]
        preview = {"id": ids[0], "dim": int(len(vec)),
                   "first_values": [round(float(v), 4) for v in vec[:8]]}

    return {
        "file": filename, "chapter": pretty_name(filename), "pages": len(pages),
        "characters": total_chars, "chunks": len(ids), "embedding_seconds": round(embed_secs, 2),
        "total_seconds": round(time.time() - t0, 2), "embedding_preview": preview,
    }


def ingest_samples() -> list[dict]:
    files = sorted(SAMPLE_DIR.glob("*.pdf"))
    if not files:
        raise FileNotFoundError("No sample PDFs found. Run: python scripts/generate_sample_pdfs.py")
    return [ingest_pdf(f.name, str(f)) for f in files]


# ---------- 5. Retrieve ----------
def retrieve(question: str, k: int = 4) -> list[dict]:
    col = get_collection()
    if col.count() == 0:
        return []
    res = col.query(query_texts=[question], n_results=min(k, col.count()),
                    include=["documents", "metadatas", "distances"])
    out = []
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        out.append({"text": doc, "chapter": meta.get("chapter"), "page": meta.get("page"),
                    "source": meta.get("source"), "score": round(max(0.0, 1 - float(dist)), 3)})
    return out


# ---------- 6. Generate with the LLM (Groq or xAI Grok - both OpenAI-compatible) ----------
SYSTEM_PROMPT = (
    "You are a friendly Python tutor. Answer the student's question using ONLY the numbered "
    "context passages from their study notes. Explain clearly in simple language, use short "
    "markdown (bullets, **bold**, fenced ```python code blocks) and cite passages like [1], [2]. "
    "If the context does not contain the answer, say you could not find it in the uploaded notes."
)

def llm_api_key() -> str | None:
    return os.getenv("LLM_API_KEY") or os.getenv("GROQ_API_KEY") or os.getenv("XAI_API_KEY")


def llm_base_url() -> str:
    url = os.getenv("LLM_BASE_URL")
    if url:
        return url
    if not os.getenv("LLM_API_KEY") and os.getenv("GROQ_API_KEY"):
        return "https://api.groq.com/openai/v1"
    return "https://api.x.ai/v1"


def llm_configured() -> bool:
    return bool(llm_api_key())


def llm_model() -> str:
    return os.getenv("GROK_MODEL") or os.getenv("LLM_MODEL") or "openai/gpt-oss-20b"


def ask_grok(question: str, contexts: list[dict]) -> str:
    from openai import OpenAI  # Groq and xAI both expose OpenAI-compatible APIs

    client = OpenAI(
        api_key=llm_api_key(),
        base_url=llm_base_url(),
    )
    context_block = "\n\n".join(
        f"[{i}] ({c['chapter']}, page {c['page']})\n{c['text']}" for i, c in enumerate(contexts, 1)
    )
    resp = client.chat.completions.create(
        model=llm_model(),
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context_block}\n\nQuestion: {question}"},
        ],
    )
    return resp.choices[0].message.content.strip()


def stats() -> dict:
    col = get_collection()
    data = col.get(include=["metadatas"])
    per_source: dict[str, dict] = {}
    for m in data["metadatas"]:
        s = per_source.setdefault(m["source"], {"chapter": m["chapter"], "chunks": 0, "pages": set()})
        s["chunks"] += 1
        s["pages"].add(m["page"])
    sources = [{"source": k, "chapter": v["chapter"], "chunks": v["chunks"], "pages": len(v["pages"])}
               for k, v in sorted(per_source.items())]
    return {"total_chunks": col.count(), "documents": len(sources), "sources": sources,
            "embedding_model": EMBEDDING_MODEL,
            "vector_db": f"ChromaDB (persistent, cosine) at {DB_DIR.name}/",
            "llm_configured": llm_configured(), "llm_model": llm_model(),
            "chunk_size": CHUNK_SIZE, "chunk_overlap": CHUNK_OVERLAP}


def browse_chunks(limit: int = 12, source: str | None = None) -> list[dict]:
    col = get_collection()
    kwargs = {"limit": limit, "include": ["documents", "metadatas", "embeddings"]}
    if source:
        kwargs["where"] = {"source": source}
    data = col.get(**kwargs)
    out = []
    for i, cid in enumerate(data["ids"]):
        vec = data["embeddings"][i]
        out.append({"id": cid, "text": data["documents"][i], "chapter": data["metadatas"][i]["chapter"],
                    "page": data["metadatas"][i]["page"], "dim": int(len(vec)),
                    "vector_preview": [round(float(v), 4) for v in vec[:6]]})
    return out


def reset() -> None:
    col = get_collection()
    ids = col.get()["ids"]
    if ids:
        col.delete(ids=ids)