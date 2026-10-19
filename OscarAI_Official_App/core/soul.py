
import os
LOG_DIR = r"C:\Users\Etern\Desktop\MetaAI_Logs"
SOUL = os.path.join(LOG_DIR, "_muse_soul.md")
def get_soul():
    try:
        return open(SOUL, 'r', encoding='utf-8', errors='ignore').read() if os.path.exists(SOUL) else "No soul yet"
    except Exception as e:
        return str(e)
