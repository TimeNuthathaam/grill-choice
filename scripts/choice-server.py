#!/usr/bin/env python3
"""
grill-choice HTTP server
Serves an archive of choice pages — a list of points each with 3 choices + comment,
plus a copy-to-clipboard summary button. LAN + Tailscale accessible.

Usage:
    python3 choice-server.py <root_dir> <port>

Endpoints:
    GET  /             -> latest.html (when present) or archive directory listing
    GET  /state?key=x  -> {"responses": {...}}
    POST /state?key=x  -> save {"responses": {...}} -> x.state.json
    GET  /urls         -> {"lan": [...], "tailscale": "100.x.x.x"}
    GET  /<file>        -> static files in root_dir

Stops on Ctrl-C.
"""
import http.server
import json
import socketserver
import sys
from functools import partial
from pathlib import Path
from urllib.parse import parse_qs, urlparse


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/" and (Path(self.directory) / "latest.html").exists():
            self._send_file("latest.html", "text/html; charset=utf-8")
        elif parsed.path == "/state":
            self._send_state(parsed.query)
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/state":
            self._save_state(parsed.query)
        else:
            self._send_json({"ok": False, "error": "not found"}, status=404)

    def _send_file(self, name, mime):
        path = Path(self.directory) / name
        if not path.exists():
            self.send_error(404, f"{name} not found")
            return
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _state_file(self, query):
        key = parse_qs(query).get("key", [""])[0]
        if not key or not key.replace("-", "").replace("_", "").isalnum():
            return None
        return Path(self.directory) / f"{key}.state.json"

    def _send_state(self, query):
        state_file = self._state_file(query)
        if state_file is None:
            self._send_json({"ok": False, "error": "invalid page key"}, status=400)
            return
        data = json.loads(state_file.read_text("utf-8")) if state_file.exists() else {"responses": {}}
        self._send_json(data)

    def _save_state(self, query):
        state_file = self._state_file(query)
        if state_file is None:
            self._send_json({"ok": False, "error": "invalid page key"}, status=400)
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        try:
            data = json.loads(body)
            state_file.write_text(
                json.dumps(data, ensure_ascii=False, indent=2), "utf-8"
            )
            self._send_json({"ok": True})
        except Exception as e:
            self._send_json({"ok": False, "error": str(e)}, status=400)

    def _send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


def main():
    if len(sys.argv) < 3:
        print("Usage: choice-server.py <root_dir> <port>", file=sys.stderr)
        sys.exit(2)
    root = Path(sys.argv[1]).resolve()
    port = int(sys.argv[2])
    if not root.exists():
        print(f"root dir not found: {root}", file=sys.stderr)
        sys.exit(2)
    # threaded: a single-threaded TCPServer stalls when a page loads several images at once
    class Server(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True

    handler = partial(Handler, directory=str(root))
    with Server(("127.0.0.1", port), handler) as httpd:
        print(f"grill-choice serving {root}", flush=True)
        print(f"  Local: http://127.0.0.1:{port}/", flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nshutting down", flush=True)


if __name__ == "__main__":
    main()
