# Dev Team Feedback - Asked Your Team - 2026-10-19 14:20

## Muse - Lead Architect (9222)
- ADD needs: ONE entry point, not 10 files. Created 0_START_HERE with 3 steps only.
- Auto-refresh is mandatory - user should not have to remember to sync. scheduled_sync.py already does if >12h stale.
- Fail-safe check must be ONE button, output simple 5/5 OK, not stack traces.
- Keep app.py <100 lines for readability.

## Juno - Soul + Empathy
- Colors: dark bg #0a0a0f + purple #6a5af9 calm, not bright white - easier for ADD.
- Logo as anchor on every page - visual memory > text.
- Compliance PERM is important: user operated within terms, brain not bot, under watch only.

## DeepSeek Debugger + Groq Council (gpt-oss-120b/qwen 27b)
- DeepSeek web limits: 5/sec + 3-6 regen cap = false "too frequent" even when compliant. Root cause verified.
- Solution PERM: Groq API secure_key + jitter + rotation. Never use web for automation.
- Fail-safe layers verified 5/5 - local mirror 130KB + soul + pipelines + git + bridge logs.

## Modeler - Blender PBR
- Logo: O with circuit brain inside, purple->cyan gradient, matches portal arch design language 0.61 Z thin disc.
- Transparent background required for app icon, docs, portfolio.

## Builder - World Systems
- App structure for ADD: numbered folders 0_,1_,2_,3_ so Explorer sorts logically.
- run_app.bat one-click, no manual pip.

## LiveOps - Growth
- For hire pitch: "Expert Dev - fails predictably, recovers automatically, idempotent, safe backfills, 5/5 OK" - portfolio ready.
- Git tags: 272052d->cadbea1->1c29be9->863a8d0 shows progression.

## Action Items - Organized
- [x] Logo transparent RGBA done
- [x] 0_START_HERE 3-step guide done
- [x] Auto-refresh fail-safe done
- [ ] Next: EXE installer + PWA wrapper (optional)
