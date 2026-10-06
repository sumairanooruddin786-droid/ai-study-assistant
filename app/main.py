"""FastAPI app - AI Study Assistant (RAG + Grok)."""
import os
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, File, HTTPException, UploadFile  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import FileResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from app import rag  # noqa: E402

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
MAX_FILE_MB = 25

app = FastAPI(title="AI Study Assistant", version="1.0.0")
origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",")]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"])


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)
    top_k: int = Field(4, ge=1, le=8)


@app.get("/api/health")
def health():
    return {"status": "ok", "llm_configured": rag.llm_configured()}


@app.post("/api/upload")
async def upload(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(400, "Please choose at least one PDF.")
    results, errors = [], []
    for f in files:
        if not (f.filename or "").lower().endswith(".pdf"):
            errors.append({"file": f.filename, "error": "Only PDF files are supported."})
            continue
        content = await f.read()
        if len(content) > MAX_FILE_MB * 1024 * 1024:
            errors.append({"file": f.filename, "error": f"File larger than {MAX_FILE_MB} MB."})
            continue
        try:
            results.append(rag.ingest_pdf(f.filename, BytesIO(content)))
        except Exception as e:  # keep going with the other files
            errors.append({"file": f.filename, "error": str(e)})
    if not results:
        raise HTTPException(400, errors[0]["error"] if errors else "Nothing was processed.")
    return {"results": results, "errors": errors, "stats": rag.stats()}


@app.post("/api/ingest-samples")
def ingest_samples():
    try:
        results = rag.ingest_samples()
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
    return {"results": results, "errors": [], "stats": rag.stats()}


@app.get("/api/stats")
def get_stats():
    return rag.stats()


@app.get("/api/chunks")
def get_chunks(limit: int = 12, source: str | None = None):
    return {"chunks": rag.browse_chunks(min(max(limit, 1), 50), source)}


@app.post("/api/ask")
def ask(req: AskRequest):
    contexts = rag.retrieve(req.question, req.top_k)
    if not contexts:
        raise HTTPException(400, "The knowledge base is empty. Upload PDFs first.")
    if not rag.llm_configured():
        # Graceful fallback so the app still works without an API key
        return {"answer": "_Grok API key not set - showing the best matching passage from your notes "
                          "(retrieval only). Add `XAI_API_KEY` to `.env` for full AI answers._\n\n"
                          + contexts[0]["text"],
                "sources": contexts, "mode": "retrieval-only"}
    try:
        answer = rag.ask_grok(req.question, contexts)
    except Exception as e:
        raise HTTPException(502, f"Grok request failed: {e}")
    return {"answer": answer, "sources": contexts, "mode": "rag-grok"}


@app.delete("/api/reset")
def reset():
    rag.reset()
    return {"status": "cleared"}


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")
