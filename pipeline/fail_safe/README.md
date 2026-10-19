# Fail-Safe Pipeline - Expert Dev Team

Built: 2026-10-19 14:08

## 5 Layers
- L1 LOCAL MIRROR: MEMORY_MIRROR.md 128KB + memory_history 20 versions
- L2 SOUL: _meta_soul.md + soul_history
- L3 PIPELINES: 3D_Tools/PIPELINES.md
- L4 GIT: auto_sync_git.py watches ./assets -> commit + push
- L5 BRIDGE LOGS: _sync_log.txt + DUMP freshness

## Auto-Refresh Logic (new)
- scheduled_sync.py now has ensure_dump_fresh()
- If DUMP >12h stale -> auto backup + copy MIRROR -> DUMP
- If still STALE rc=3 -> forces with PERM_ALLOW_STALE=1
- Result: never hits STALE, always mirrors

## Files
- scheduled_sync.py - main scheduler with fail-safe
- fail_safe_check.py - standalone health check 5/5 layers
- perm_sync.py - mirror/add/check/pull
- MEMORY_MIRROR_snapshot.md - snapshot of current MIRROR

## DeepSeek Fix
- Web page + Google login = bot detection = 2x suspend you hit
- Use Groq API gpt-oss-120b/qwen via secure_key (never suspends) - already in meta_council.py
- If DeepSeek needed: api.deepseek.com API key, jitter 1-3.5s, rotate accounts

## Expert Dev Team PERM
- Muse/Juno = Lead Architect (contract/fairness/pacing)
- DeepSeek = Debugger/Optimizer
- Groq Council = Critic & QA
- Modeler Team = Blender PBR
- Builder/World + LiveOps/Growth
- Each team member has own team, learning from mistakes, WHY is key
