import http.server
import os
import threading
import socketserver

PORT = 8000

Handler = http.server.SimpleHTTPRequestHandler

class HTTPServerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def run(self):
        print(os. getcwd())
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print("serving at port", PORT)
            httpd.serve_forever()

http_server_thread = HTTPServerThread()
