
import http.server, socketserver, os, json, sys, subprocess, time
from urllib.parse import urlparse, parse_qs
APP = r"C:\Users\Etern\Desktop\OscarAI_Official_App"
LOG_DIR = r"C:\Users\Etern\Desktop\MetaAI_Logs"
MIRROR = os.path.join(LOG_DIR, "MEMORY_MIRROR.md")

def get_status():
    try:
        mtime = os.path.getmtime(MIRROR) if os.path.exists(MIRROR) else 0
        age = (time.time()-mtime)/3600 if mtime else 999
        size = os.path.getsize(MIRROR) if os.path.exists(MIRROR) else 0
        return {"mirror_bytes": size, "age_h": round(age,2), "fresh": age < 12}
    except Exception as e:
        return {"error": str(e)}

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path.startswith("/?"):
            status = get_status()
            html = open(os.path.join(APP, "templates", "index.html"), 'r', encoding='utf-8', errors='ignore').read()
            # simple replace for mem
            html = html.replace("{{ mem.mirror_bytes }}", str(status.get("mirror_bytes",0)))
            html = html.replace("{{ mem.mirror_age_h }}", str(status.get("age_h",0)))
            html = html.replace("{{ mem.dump_age_h }}", str(status.get("age_h",0)))
            # strip jinja loops for fallback
            self.send_response(200)
            self.send_header("Content-type","text/html")
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        elif self.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-type","application/json")
            self.end_headers()
            self.wfile.write(json.dumps(get_status()).encode())
        elif self.path == "/api/fail_safe":
            out = "Run fail_safe_check.py: "
            try:
                r = subprocess.run([sys.executable, os.path.join(LOG_DIR, "fail_safe_check.py")], capture_output=True, text=True, timeout=10)
                out = r.stdout + r.stderr
            except Exception as e:
                out = str(e)
            self.send_response(200)
            self.send_header("Content-type","application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"output": out}).encode())
        else:
            return super().do_GET()
    def do_POST(self):
        if self.path == "/api/sync":
            out = ""
            try:
                r = subprocess.run([sys.executable, os.path.join(LOG_DIR, "scheduled_sync.py")], capture_output=True, text=True, timeout=30)
                out = r.stdout + r.stderr
            except Exception as e:
                out = str(e)
            self.send_response(200)
            self.send_header("Content-type","application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"output": out[-3000:]}).encode())
        else:
            self.send_response(404)
            self.end_headers()

os.chdir(APP)
PORT = 8765
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving OscarAI Official App at http://127.0.0.1:{PORT}")
    httpd.serve_forever()
