#!/usr/bin/env python3
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


port = int(os.environ["NODE_PORT"])
with open("/dev/shm/remnanode-test-start.json", "w", encoding="utf-8") as output:
    json.dump({
        "port": port,
        "custom_core_url": os.environ.get("CUSTOM_CORE_URL", ""),
        "secret_present": bool(os.environ.get("SECRET_KEY")),
    }, output)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, _format, *_args):
        return


ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
