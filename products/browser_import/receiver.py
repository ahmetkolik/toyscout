import http.server, json, os, sys
D=sys.argv[1]
class H(http.server.BaseHTTPRequestHandler):
    def _c(self):
        self.send_header('Access-Control-Allow-Origin','*'); self.send_header('Access-Control-Allow-Headers','*'); self.send_header('Access-Control-Allow-Methods','POST,OPTIONS')
    def do_OPTIONS(self): self.send_response(204); self._c(); self.end_headers()
    def do_GET(self):
        if self.path.startswith('/sleep'):
            import time,random; time.sleep(1.5+random.random()*1.0)
            self.send_response(200); self._c(); self.end_headers(); self.wfile.write(b'z'); return
        b=open(os.path.join(os.path.dirname(D),'cands.json'),'rb').read()
        self.send_response(200); self._c(); self.send_header('Content-Type','application/json'); self.end_headers(); self.wfile.write(b)
    def do_POST(self):
        b=self.rfile.read(int(self.headers.get('content-length',0)))
        try: a=json.loads(b)['asin']
        except Exception: a='bad'
        open(os.path.join(D,a+'.json'),'wb').write(b)
        self.send_response(200); self._c(); self.end_headers(); self.wfile.write(b'ok')
    def log_message(self,*a): pass
http.server.ThreadingHTTPServer(('127.0.0.1',8765),H).serve_forever()
