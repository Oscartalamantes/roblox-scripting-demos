
import os, subprocess, sys, time
LOG_DIR = r"C:\Users\Etern\Desktop\MetaAI_Logs"
LOG = os.path.join(LOG_DIR, "_sync_log.txt")
SCHED = os.path.join(LOG_DIR, "scheduled_sync.py")
FAIL = os.path.join(LOG_DIR, "fail_safe_check.py")

def run_fail_safe():
    try:
        r = subprocess.run([sys.executable, FAIL], capture_output=True, text=True, timeout=15)
        return r.stdout
    except Exception as e:
        return str(e)

def run_sync():
    try:
        r = subprocess.run([sys.executable, SCHED], capture_output=True, text=True, timeout=60)
        return r.stdout + "\n" + r.stderr
    except Exception as e:
        return str(e)

def get_log_tail(n=50):
    try:
        lines = open(LOG, 'r', encoding='utf-8', errors='ignore').read().splitlines()[-n:]
        return "\n".join(lines)
    except:
        return "No log"
