
from http.server import BaseHTTPRequestHandler, HTTPServer
import os, time, urllib.parse
import sys#; sys.path.append('/home/ibrahem/Desktop/Code/Projects/OnTime Shop') #import my UDF
import mimetypes
from threading import Thread

def init_local_http(root=None, accept_outer_connection=False):
    # root is: the root path directory that the server serves up.
    # accept_outer_connection is: whether you want to serve up
    #  connections comming from outside of 127.0.0.1
    #  ie: from other devices in local network or global one
    if root:
        if not os.path.exists(root):
            raise FileNotFoundError('root directory was not found')
        root = os.path.relpath(root)
        pathes = []
        for path in sys.path:
            pathes.append(
                os.path.join(path, root)
            )
    else:
        pathes = sys.path

    class http_handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if '?' in self.path: self.path = self.path.split('?')[0]
            self.path = urllib.parse.unquote(self.path)
            # print(self.path) #d
            if accept_outer_connection:
                accept_connection = True
            else:
                if self.client_address[0] != "127.0.0.1":
                    accept_connection = False #reject connections from outside localhost
                else: accept_connection = True
            if accept_connection: 
                if self.path == '/': self.path = "/index.html"
                for path in pathes:
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
            time.sleep(0.5) # wait for server to run
            return port
        except: continue

if __name__ == "__main__": #test code
    init_local_http()
    while 1: time.sleep(9)
