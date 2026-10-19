# OscarAI - Official App
Built: 2026-10-19 14:15
Expert Dev - Oscar Talamantes

## Run
pip install -r requirements.txt
python app.py
Open http://127.0.0.1:8765

## Architecture - Team-of-Teams
- Muse/Juno Lead Architect 9222
- DeepSeek Debugger/Optimizer + Groq Council gpt-oss-120b/qwen fallback
- Modeler Blender PBR
- Builder/World + LiveOps/Growth
- Each team has own sub-team, learns from MISTAKES LOG, WHY is key

## Fail-Safe 5 Layers (your pipeline)
1. LOCAL MIRROR MEMORY_MIRROR.md 130KB + 20 history
2. SOUL _muse_soul.md
3. PIPELINES 3D_Tools/PIPELINES.md
4. GIT 1c29be9 auto-sync
5. BRIDGE LOGS + auto-refresh if dump >12h stale - never STALE

## Compliance
Within terms/policy, AI helped understand + streamlined, automated under watch only.
DeepSeek web: 5/sec + 3-6 regen cap -> false too frequent + server busy.
Solution: Groq API secure_key, DeepSeek API api.deepseek.com with jitter/rotation.

## For Hire
Portfolio app demonstrating Expert Dev pipeline that fails predictably, recovers automatically, idempotent, safe backfills, 5/5 OK.
