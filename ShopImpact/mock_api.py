from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # quiet the default logging to keep the terminal cleaner
        return

if __name__ == "__main__":
    port = 8000
    print(f"Mock API server listening on http://localhost:{port}")
    httpd = HTTPServer(("0.0.0.0", port), Handler)
    httpd.serve_forever()
