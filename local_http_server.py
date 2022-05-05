
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import sys#; sys.path.append('/home/ibrahem/Desktop/Code/Projects/OnTime Shop') #import my UDF
import mimetypes
from threading import Thread

def init_local_http():
    class http_handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if '?' in self.path: self.path = self.path.split('?')[0]
            # print(self.path) #d
            if self.client_address[0] == "127.0.0.1": #reject connections from outside localhost
                if self.path == '/': self.path = "/index.html"
                for path in sys.path:
                    if os.path.exists(path+self.path):
                        cont = open(path+self.path, 'rb').read()
                        self.send_response(200)
                        self.send_header('Content-Type', mimetypes.guess_type(self.path, strict=False)[0])
                        self.end_headers()
                        self.wfile.write(cont)
                        return
                cont = b'404'
                self.send_response(404)
                self.end_headers()
                self.wfile.write(cont)
                print(f'[404]: {self.path}')
            else:
                cont = b'Forbidden'
                self.send_response(403)
                self.end_headers()
                self.wfile.write(cont)

        def log_message(self, format, *args): return
    def launch_server(server):
        try: server.serve_forever()
        except: server.server_close()
    for port in range(1025, 65535):  # check for all available ports
        try:
            server = HTTPServer(("", port), http_handler)
            Thread(target=launch_server, args=([server])).start()
            return port
        except: continue

if __name__ == "__main__": #test code
    import time
    init_local_http()
    while 1: time.sleep(9)
