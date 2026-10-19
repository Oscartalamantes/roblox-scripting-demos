
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from core.memory import get_memory_status
from core.soul import get_soul
from core.pipeline import run_fail_safe, run_sync, get_log_tail
from core.council import get_teams

app = FastAPI(title="OscarAI - Official App")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    mem = get_memory_status()
    soul = get_soul()[:3000]
    teams = get_teams()
    log = get_log_tail(30)
    return templates.TemplateResponse("index.html", {"request": request, "mem": mem, "soul": soul, "teams": teams, "log": log})

@app.get("/api/status")
def status():
    return get_memory_status()

@app.get("/api/fail_safe")
def fail_safe():
    return {"output": run_fail_safe()}

@app.post("/api/sync")
def sync():
    return {"output": run_sync()}

@app.get("/api/soul")
def soul_api():
    return {"soul": get_soul()}

@app.get("/api/teams")
def teams_api():
    return get_teams()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8765)
