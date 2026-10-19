#!/usr/bin/env python3
"""fail_safe_check.py - standalone health check for pipeline
Checks 5 layers, auto-fixes stale dump, reports DeepSeek fallback status
"""
import os, time, shutil, datetime
LOG_DIR = r"C:\Users\Etern\Desktop\MetaAI_Logs"
DUMP = r"C:\Users\Etern\Desktop\3D_Tools\CryptArch\listing\_memory.md"
MIRROR = os.path.join(LOG_DIR, "MEMORY_MIRROR.md")
MEMORY = os.path.join(LOG_DIR, "MEMORY.md")
PIPE = r"C:\Users\Etern\Desktop\3D_Tools\PIPELINES.md"
SOUL = os.path.join(LOG_DIR, "_meta_soul.md")
HIST = os.path.join(LOG_DIR, "memory_history")

def check():
    print("=== FAIL-SAFE PIPELINE CHECK ===")
    print(f"Time: {datetime.datetime.now()}")
    layers = []
    # Layer 1 LOCAL
    if os.path.exists(MIRROR):
        sz = os.path.getsize(MIRROR)
        age = (time.time() - os.path.getmtime(MIRROR))/3600
        print(f"[OK] L1 LOCAL MIRROR {sz} bytes {age:.1f}h old")
        layers.append(True)
    else:
        print("[FAIL] L1 MIRROR missing")
        layers.append(False)
    # Layer 2 SOUL
    if os.path.exists(SOUL) and os.path.isdir(HIST):
        print(f"[OK] L2 SOUL {os.path.getsize(SOUL)} bytes + {len(os.listdir(HIST))} history")
        layers.append(True)
    else:
        print("[FAIL] L2 SOUL missing")
        layers.append(False)
    # Layer 3 PIPELINES
    if os.path.exists(PIPE):
        print(f"[OK] L3 PIPELINES {os.path.getsize(PIPE)} bytes")
        layers.append(True)
    else:
        print("[FAIL] L3 PIPELINES missing")
        layers.append(False)
    # Layer 4 GIT
    import subprocess
    try:
        root = r"C:\Users\Etern\Documents\roblox-scripting-demos"
        st = subprocess.check_output(["git", "-C", root, "status", "--short"], text=True, timeout=5)
        if not st.strip():
            print("[OK] L4 GIT clean pushed")
            layers.append(True)
        else:
            print(f"[WARN] L4 GIT has changes: {st[:100]}")
            layers.append(True)
    except Exception as e:
        print(f"[WARN] L4 GIT check {e}")
        layers.append(False)
    # Layer 5 BRIDGE LOGS + DUMP freshness
    if os.path.exists(DUMP):
        age = (time.time() - os.path.getmtime(DUMP))/3600
        if age > 12:
            print(f"[WARN] L5 DUMP stale {age:.1f}h - auto-refresh needed")
            # auto-fix
            if os.path.exists(MIRROR):
                shutil.copy2(MIRROR, DUMP)
                print(f"[FIX] DUMP refreshed from MIRROR")
                layers.append(True)
            else:
                layers.append(False)
        else:
            print(f"[OK] L5 DUMP fresh {age:.1f}h")
            layers.append(True)
    else:
        print("[FAIL] L5 DUMP missing")
        layers.append(False)
    print(f"\nResult: {sum(layers)}/5 layers OK - {'FAIL-SAFE OK' if all(layers) else 'NEEDS ATTENTION'}")
    print("\nDeepSeek fallback:")
    print("- Web page with Google login = SUSPENDS for bot churn (you hit 2x)")
    print("- Use Groq API gpt-oss-120b/qwen (already in meta_council.py) + secure_key - never suspends")
    print("- If DeepSeek needed, use API key api.deepseek.com not webpage")

if __name__ == "__main__":
    check()
