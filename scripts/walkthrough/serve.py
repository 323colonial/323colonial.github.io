"""Local preview server: python3 scripts/walkthrough/serve.py [port]

Like `python3 -m http.server`, but with a deeper listen queue (the game opens
about fifty requests at once, which the stock server drops) and no caching.
"""
import http.server, os, sys, threading

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


class Handler(http.server.SimpleHTTPRequestHandler):
    note_lock = threading.Lock()  # ponytail: serialize local note writes; use a store if multi-user.

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *a):
        pass

    def do_POST(self):
        """K in the game posts here: the spot is appended to .walkthrough-notes/notes.txt and
        the view saved beside it as NNN.jpg, so problem views can be read back later."""
        if self.path != "/__note":
            self.send_error(404)
            return
        import base64, binascii, json, time
        host = self.headers.get("Host", "")
        port = self.server.server_address[1]
        if host not in (f"127.0.0.1:{port}", f"localhost:{port}") or self.headers.get("Origin") != "http://" + host:
            self.send_error(403, "Same-origin local preview requests only")
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 4 * 1024 * 1024:
                self.send_error(413)
                return
            d = json.loads(self.rfile.read(size))
            if not isinstance(d, dict) or not isinstance(d.get("note"), str) or len(d["note"]) > 8000:
                raise ValueError("Invalid note")
            image = d.get("image", "")
            if not isinstance(image, str) or not image.startswith("data:image/jpeg;base64,"):
                raise ValueError("JPEG required")
            image = base64.b64decode(image.split(",", 1)[1], validate=True)
            if not image.startswith(b"\xff\xd8\xff"):
                raise ValueError("Invalid JPEG")
        except (ValueError, UnicodeError, binascii.Error):
            self.send_error(400, "Invalid note payload")
            return
        try:
            with self.note_lock:
                os.makedirs(".walkthrough-notes", exist_ok=True)
                n = max((int(f[:-4]) for f in os.listdir(".walkthrough-notes")
                         if f.endswith(".jpg") and f[:-4].isdigit()), default=0) + 1
                with open(".walkthrough-notes/%03d.jpg" % n, "xb") as f:
                    f.write(image)
                with open(".walkthrough-notes/notes.txt", "a", encoding="utf-8") as f:
                    f.write("%03d  %s  %s\n" % (n, time.strftime("%H:%M:%S"), " ".join(d["note"].splitlines())))
        except OSError:
            self.send_error(500, "Could not save note")
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"n": n}).encode())


class Server(http.server.ThreadingHTTPServer):
    request_queue_size = 256
    daemon_threads = True


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8377
    print("http://127.0.0.1:%d/walkthrough/" % port, flush=True)
    Server(("127.0.0.1", port), Handler).serve_forever()
