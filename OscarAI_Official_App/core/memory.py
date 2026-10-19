
import os, time
LOG_DIR = r"C:\Users\Etern\Desktop\MetaAI_Logs"
MIRROR = os.path.join(LOG_DIR, "MEMORY_MIRROR.md")
DUMP = r"C:\Users\Etern\Desktop\3D_Tools\CryptArch\listing\_memory.md"

def get_memory_status():
    try:
        mtime = os.path.getmtime(MIRROR) if os.path.exists(MIRROR) else 0
        dtime = os.path.getmtime(DUMP) if os.path.exists(DUMP) else 0
        age_m = (time.time()-mtime)/3600 if mtime else 999
        age_d = (time.time()-dtime)/3600 if dtime else 999
        size = os.path.getsize(MIRROR) if os.path.exists(MIRROR) else 0
        content = open(MIRROR, 'r', encoding='utf-8', errors='ignore').read()[-5000:] if os.path.exists(MIRROR) else "No mirror"
        return {"mirror_age_h": round(age_m,2), "dump_age_h": round(age_d,2), "mirror_bytes": size, "tail": content}
    except Exception as e:
        return {"error": str(e)}
