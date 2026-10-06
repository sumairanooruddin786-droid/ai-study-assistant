# AI Study Assistant (RAG + Embeddings + Grok)

Ask questions about 5 Python PDF chapters. The app extracts text, splits it into chunks, creates
embeddings, stores them locally in **ChromaDB**, retrieves the most relevant chunks for each question
and sends them to **Grok (xAI)** to write the final answer. Built with a FastAPI backend and a custom
HTML/CSS/JS frontend.

## Architecture
PDF upload -> pypdf text extraction -> overlapping chunks (600 chars / 100 overlap) -> MiniLM embeddings
(384-dim, ChromaDB default) -> ChromaDB (persistent, cosine) -> top-k retrieval -> Grok -> answer + sources.

## Run locally
```bash
python -m venv venv
venv\Scripts\activate            # Windows   (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env           # macOS/Linux: cp .env.example .env  -> put your XAI_API_KEY inside
python scripts/generate_sample_pdfs.py     # optional: recreates the 5 sample chapters
python -m uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000 . The first run downloads the small embedding model (~80 MB) once.

## Using the app
1. Click **Use sample chapters** (or drop your own 5 PDFs and click **Process PDFs**).
2. Watch the 5 pipeline steps complete (screenshots: PDF upload, embeddings creation).
3. Open the **Vector database** tab (screenshot: saved vector DB; the `chroma_db/` folder also exists on disk).
4. Ask at least 3 questions (screenshots of the AI answers).

## API
| Method | Path | Purpose |
|---|---|---|
| POST | /api/upload | upload PDFs, run the full pipeline |
| POST | /api/ingest-samples | process the bundled sample chapters |
| GET | /api/stats, /api/chunks | inspect the vector DB |
| POST | /api/ask | `{question, top_k}` -> answer + sources |
| DELETE | /api/reset | clear the vector DB |

Interactive docs: `/docs`.

## Deployment
ChromaDB needs a long-running Python process, so the **backend** goes on a Python host (Render - see
`render.yaml`; set `XAI_API_KEY` in its environment). The **frontend** (`static/`) can be hosted on
Firebase Hosting and/or Vercel; set `window.API_BASE` in `static/config.js` to the backend URL first.

- Firebase: `npm i -g firebase-tools`, `firebase login`, `firebase init hosting` (public dir `static`), `firebase deploy`
- Vercel: `npm i -g vercel`, then `vercel --prod` from this folder (`vercel.json` serves `static/`)

Free Render disks are ephemeral: after a restart click **Use sample chapters** again.
