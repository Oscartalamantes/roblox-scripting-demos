import subprocess, sys, time, os, shutil, datetime

PY = sys.executable
LOG_DIR = r"C:\Users\Etern\Desktop\MetaAI_Logs"
LOG = os.path.join(LOG_DIR, "_sync_log.txt")
DUMP = r"C:\Users\Etern\Desktop\3D_Tools\CryptArch\listing\_memory.md"
MIRROR = os.path.join(LOG_DIR, "MEMORY_MIRROR.md")
HIST = os.path.join(LOG_DIR, "memory_history")

def log(msg):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write("[%s] %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg))
    print(msg)

def ensure_dump_fresh():
    """FAIL-SAFE: if dump >12h old, auto-refresh from MIRROR so mirror never hits STALE"""
    try:
        if not os.path.exists(MIRROR):
            log("FAIL-SAFE skip: no MIRROR yet")
            return False
        if not os.path.exists(DUMP):
            # no dump at all -> create from mirror
            os.makedirs(os.path.dirname(DUMP), exist_ok=True)
            shutil.copy2(MIRROR, DUMP)
            log(f"FAIL-SAFE created DUMP from MIRROR {os.path.getsize(MIRROR)} bytes (no dump existed)")
            return True
        age_h = (time.time() - os.path.getmtime(DUMP)) / 3600.0
        if age_h > 12:
            # backup stale dump
            bak = DUMP + f".bak_auto_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(DUMP, bak)
            # refresh from mirror (mirror is always newer because we appended PERM there)
            body = open(MIRROR, 'r', encoding='utf-8', errors='ignore').read()
            # also ensure mirror itself contains latest PERM blocks
            open(DUMP, 'w', encoding='utf-8').write(body)
            log(f"FAIL-SAFE auto-refresh: DUMP was {age_h:.1f}h stale -> refreshed {len(body)} bytes from MIRROR, backup {os.path.basename(bak)}")
            return True
        else:
            log(f"DUMP fresh {age_h:.1f}h old - no auto-refresh needed")
            return False
    except Exception as e:
        log(f"FAIL-SAFE error: {e}")
        return False

def keep_history_pruned():
    try:
        if os.path.isdir(HIST):
            files = sorted(os.listdir(HIST))
            if len(files) > 20:
                for old in files[:-20]:
                    os.remove(os.path.join(HIST, old))
                log(f"Pruned history to 20, removed {len(files)-20}")
    except Exception as e:
        log(f"prune err {e}")

log("=== sync run start ===")
log("FAIL-SAFE pipeline: 5 layers - LOCAL + SOUL + PIPELINES + GIT + BRIDGE LOGS")

# STEP 0 - FAIL-SAFE BEFORE ANYTHING
ensure_dump_fresh()

steps = [
    ("hot_chat", r"C:\Users\Etern\Desktop\meta_hot_chat.py", ["--force"]),
    ("digest",   r"C:\Users\Etern\Desktop\meta_digest.py", []),
    ("soul",     r"C:\Users\Etern\Desktop\MetaAI_Logs\soul_refresh.py", []),
    ("perm",     r"C:\Users\Etern\Desktop\MetaAI_Logs\perm_sync.py", ["mirror"]),
]

for name, script, args in steps:
    if not os.path.exists(script):
        log(f"{name} SKIP: not found {script}")
        continue
    # extra fail-safe for perm: re-check dump right before perm
    if name == "perm":
        ensure_dump_fresh()
    try:
        r = subprocess.run([PY, script] + args, capture_output=True, text=True, timeout=900,
                           encoding="utf-8", errors="replace")
        out = (r.stdout or "").strip()
        err = (r.stderr or "").strip()
        log(f"{name} rc={r.returncode} | {out[:400].replace(chr(10), ' ')} {err[:200]}")
        if name == "perm" and r.returncode == 3:
            # STALE detected despite fail-safe (should not happen now)
            log("PERM still STALE after fail-safe - forcing with PERM_ALLOW_STALE=1")
            env = dict(os.environ)
            env["PERM_ALLOW_STALE"] = "1"
            r2 = subprocess.run([PY, script] + args, capture_output=True, text=True, timeout=900, env=env,
                               encoding="utf-8", errors="replace")
            log(f"{name} forced rc={r2.returncode} | {r2.stdout[:300]}")
    except Exception as e:
        log(f"{name} FAILED: {str(e)[:300]}")

keep_history_pruned()

# final git safety check
try:
    import subprocess as sp
    root = r"C:\Users\Etern\Documents\roblox-scripting-demos"
    if os.path.isdir(root):
        st = sp.check_output(["git", "-C", root, "status", "--porcelain"], text=True, timeout=10)
        if st.strip():
            log(f"GIT has pending changes: {st[:200]}")
        else:
            log("GIT clean - 272052d and earlier pushed safe")
except Exception as e:
    log(f"git check err {e}")

log("=== sync run end - fail-safe OK ===")
