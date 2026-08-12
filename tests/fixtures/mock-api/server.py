#!/usr/bin/env python3
import json
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse


def initial_state():
    return {
        "public_ip": "198.51.100.10",
        "inbounds": [
            {"uuid": "inbound-a", "tag": "VLESS_TCP_REALITY_NGINX"},
            {"uuid": "inbound-b", "tag": "TCP_TLS_NGINX"},
        ],
        "nodes": [],
        "dns_records": [],
        "requests": [],
        "failures": {},
        "keygen_count": 0,
    }


STATE = initial_state()
LOCK = threading.Lock()


def normalized_node(body):
    node = dict(body)
    node.setdefault("uuid", f"node-{uuid.uuid4().hex[:8]}")
    profile = dict(node.get("configProfile") or {})
    profile["activeInbounds"] = [
        value if isinstance(value, dict) else {"uuid": value}
        for value in profile.get("activeInbounds", [])
    ]
    node["configProfile"] = profile
    return node


class Handler(BaseHTTPRequestHandler):
    server_version = "rw-test-api/1"

    def log_message(self, _format, *_args):
        return

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if not length:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def send_json(self, status, body):
        payload = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def send_text(self, status, body, content_type="text/plain"):
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def request_key(self, path):
        return f"{self.command} {path}"

    def maybe_fail(self, path):
        failure = STATE["failures"].get(self.request_key(path))
        if not failure:
            return False
        status = int(failure.get("status", 500))
        if "raw" in failure:
            self.send_text(status, str(failure["raw"]), failure.get("content_type", "application/json"))
        else:
            self.send_json(status, failure.get("body", {"error": "injected failure"}))
        return True

    def record(self, path, body=None):
        STATE["requests"].append({"method": self.command, "path": path, "body": body})

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        with LOCK:
            if path == "/admin/state":
                self.send_json(200, STATE)
                return
            self.record(path)
            if self.maybe_fail(path):
                return
            if path == "/ip":
                self.send_text(200, STATE["public_ip"])
                return
            if path.startswith("/api/config-profiles/") and path.endswith("/inbounds"):
                self.send_json(200, {"response": {"inbounds": STATE["inbounds"]}})
                return
            if path == "/api/nodes":
                self.send_json(200, {"response": STATE["nodes"]})
                return
            if path == "/api/keygen":
                STATE["keygen_count"] += 1
                self.send_json(200, {"response": {"secretKey": f"test-secret-{STATE['keygen_count']:04d}"}})
                return
            if path.endswith("/dns_records"):
                query = parse_qs(parsed.query)
                name = unquote(query.get("name", [""])[0])
                record_type = query.get("type", [""])[0]
                records = [
                    record for record in STATE["dns_records"]
                    if record.get("type") == record_type and record.get("name") == name
                ]
                self.send_json(200, {"success": True, "result": records})
                return
            self.send_json(404, {"error": "not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        body = self.read_json()
        with LOCK:
            if path == "/admin/reset":
                STATE.clear()
                STATE.update(initial_state())
                for key, value in body.items():
                    STATE[key] = value
                self.send_json(200, {"ok": True})
                return
            self.record(path, body)
            if self.maybe_fail(path):
                return
            if path == "/api/nodes":
                node = normalized_node(body)
                STATE["nodes"].append(node)
                self.send_json(201, {"response": node})
                return
            if path.endswith("/dns_records"):
                record = dict(body)
                record["id"] = f"dns-{uuid.uuid4().hex[:8]}"
                STATE["dns_records"].append(record)
                self.send_json(200, {"success": True, "result": record})
                return
            self.send_json(404, {"error": "not found"})

    def do_PATCH(self):
        path = urlparse(self.path).path
        body = self.read_json()
        with LOCK:
            self.record(path, body)
            if self.maybe_fail(path):
                return
            if path == "/api/nodes":
                wanted = body.get("uuid")
                for index, current in enumerate(STATE["nodes"]):
                    if current.get("uuid") == wanted:
                        merged = dict(current)
                        merged.update(body)
                        STATE["nodes"][index] = normalized_node(merged)
                        self.send_json(200, {"response": STATE["nodes"][index]})
                        return
                self.send_json(404, {"error": "node not found"})
                return
            self.send_json(404, {"error": "not found"})

    def do_PUT(self):
        path = urlparse(self.path).path
        body = self.read_json()
        with LOCK:
            self.record(path, body)
            if self.maybe_fail(path):
                return
            if "/dns_records/" in path:
                record_id = path.rsplit("/", 1)[-1]
                for index, current in enumerate(STATE["dns_records"]):
                    if current.get("id") == record_id:
                        updated = dict(body)
                        updated["id"] = record_id
                        STATE["dns_records"][index] = updated
                        self.send_json(200, {"success": True, "result": updated})
                        return
                self.send_json(404, {"success": False, "errors": [{"message": "record not found"}]})
                return
            self.send_json(404, {"error": "not found"})


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
