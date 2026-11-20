"""Small web app: paste a video link (or upload a file), watch progress, download results.

Run:  uvicorn media_extractor.web:app --host 0.0.0.0 --port 8000
Data: $MEDIA_EXTRACTOR_DATA (default ./downloads/jobs)
"""
from __future__ import annotations

import os
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse

from .pipeline import is_url, process

DATA_DIR = Path(os.environ.get("MEDIA_EXTRACTOR_DATA", "downloads/jobs")).resolve()
DATA_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Media Extractor")
_pool = ThreadPoolExecutor(max_workers=2)
_jobs: dict[str, dict] = {}
_lock = threading.Lock()


def _set(job_id: str, **fields) -> None:
    with _lock:
        _jobs[job_id].update(fields)


def _run_job(job_id: str, source: str, job_dir: Path, options: dict) -> None:
    try:
        manifest = process(source, job_dir, progress=lambda msg: _set(job_id, stage=msg), **options)
        _set(job_id, status="done", stage="done", manifest=manifest)
    except Exception as exc:
        _set(job_id, status="error", stage="error", error=str(exc)[-1500:])


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return PAGE


@app.post("/api/jobs")
async def create_job(
    url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    events: bool = Form(True),
    scenes: bool = Form(True),
    separate: bool = Form(False),
) -> dict:
    job_id = uuid.uuid4().hex[:12]
    job_dir = DATA_DIR / job_id
    job_dir.mkdir(parents=True)
    if file is not None and file.filename:
        source = str(job_dir / ("upload" + (Path(file.filename).suffix.lower() or ".mp4")))
        with open(source, "wb") as fh:
            while chunk := await file.read(1024 * 1024):
                fh.write(chunk)
    elif url and is_url(url.strip()):
        source = url.strip()
    else:
        raise HTTPException(400, "Give a video link (http/https) or upload a video file")
    with _lock:
        _jobs[job_id] = {"id": job_id, "status": "running", "stage": "queued", "source": source if not source.startswith(str(job_dir)) else "upload"}
    _pool.submit(_run_job, job_id, source, job_dir, {"events": events, "scenes": scenes, "separate": separate})
    return {"job_id": job_id}


@app.get("/api/jobs/{job_id}")
def job_status(job_id: str) -> dict:
    with _lock:
        job = _jobs.get(job_id)
    if job is None:
        raise HTTPException(404, "unknown job")
    return job


@app.get("/files/{job_id}/{path:path}")
def job_file(job_id: str, path: str) -> FileResponse:
    base = (DATA_DIR / job_id).resolve()
    target = (base / path).resolve()
    if base not in target.parents or not target.is_file():
        raise HTTPException(404, "not found")
    return FileResponse(target)


PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>Media Extractor</title>
<style>body{font-family:system-ui,sans-serif;max-width:860px;margin:32px auto;padding:0 16px;color:#111}
input[type=text]{width:100%;padding:10px;font-size:16px}button{padding:10px 18px;font-size:16px;margin-top:8px}
pre{background:#f5f5f5;padding:12px;overflow:auto;max-height:340px}a{color:#0b5fff}.muted{color:#666}</style></head>
<body><h2>Media Extractor</h2>
<p class="muted">Video link do ya file upload karo. Video, audio, sound events (SFX clips), scene keyframes aur manifest milega.
Sirf wo content use karo jis ke rights tumhare paas hon.</p>
<form id="f">
<input type="text" id="url" placeholder="https://www.youtube.com/watch?v=..."><br>
<p>ya file: <input type="file" id="file" accept="video/*"></p>
<label><input type="checkbox" id="events" checked> sound events / SFX clips</label>
<label><input type="checkbox" id="scenes" checked> scenes + keyframes</label>
<label><input type="checkbox" id="separate"> vocals vs music (demucs, heavy)</label><br>
<button>Start</button></form>
<h3>Status</h3><pre id="status">idle</pre>
<h3>Files</h3><div id="files"></div>
<script>
const s = document.getElementById('status'), files = document.getElementById('files');
document.getElementById('f').addEventListener('submit', async (e) => {
  e.preventDefault(); files.innerHTML = '';
  const fd = new FormData();
  fd.append('url', document.getElementById('url').value);
  const file = document.getElementById('file').files[0]; if (file) fd.append('file', file);
  fd.append('events', document.getElementById('events').checked);
  fd.append('scenes', document.getElementById('scenes').checked);
  fd.append('separate', document.getElementById('separate').checked);
  const r = await fetch('/api/jobs', {method: 'POST', body: fd});
  if (!r.ok) { s.textContent = await r.text(); return; }
  const {job_id} = await r.json();
  const timer = setInterval(async () => {
    const j = await (await fetch('/api/jobs/' + job_id)).json();
    s.textContent = JSON.stringify({status: j.status, stage: j.stage, error: j.error}, null, 2);
    if (j.status !== 'running') {
      clearInterval(timer);
      if (j.status === 'done') {
        const m = j.manifest; const names = [m.files.video, m.files.audio_mp3, m.files.audio_wav, 'manifest.json'];
        if (m.files.sfx_dir) names.push('sfx/');
        files.innerHTML = names.map(n => n.endsWith('/') ? '<div class="muted">' + n + ' (folder, see manifest)</div>' :
          '<div><a href="/files/' + job_id + '/' + n + '">' + n + '</a></div>').join('');
        s.textContent = JSON.stringify({status: 'done', duration_s: m.duration_s, events: (m.events||[]).length, scenes: (m.scenes||[]).length}, null, 2);
      }
    }
  }, 2000);
});
</script></body></html>"""
