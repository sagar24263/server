from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import requests
import os
import threading
from socketserver import ThreadingMixIn


form = '''<!DOCTYPE html>
    <h1> URL Shortner </h1>
    <form method = "POST">
    <label for = 'LongURI'>Long URI: </label>
    <input name='LongURI'>

    <br>

    <label for = 'ShortURI'>Short URI: </label>
    <input name='ShortURI'>
    <br>
    <button type='submit'>Submit</button>
    </form>
<pre>
{}
</pre>
'''

memory = {}

def uricheck(url):
    r = requests.get(url)
    return r.status_code == 200


class Shortner(BaseHTTPRequestHandler):
    def do_GET(self):
        name = self.path[1:]

        if name:
            if name in memory:
                self.send_response(303)
                self.send_header("Location",memory[name])
                self.end_headers()
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write("I don't know '{}'.".format(name).encode())
        else:

            self.send_response(200)
            self.send_header("Content-type","text/html; charset=utf-8")

            self.end_headers()
            # self.wfile.write(form.encode())

            s = '\n'.join("{} : {}".format(key, memory[key]) for key in memory.keys())
            self.wfile.write(form.format(s).encode())
            

    def do_POST(self):
        length = int(self.headers.get('Content-Length',0))
        body = self.rfile.read(length).decode()
        parameters = parse_qs(body)
        
        if "LongURI" not in parameters or "ShortURI" not in parameters:
            self.send_response(400)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write("Missing form fields!".encode())
            return
        
        longuri = parameters["LongURI"][0]
        shorturi = parameters["ShortURI"][0]

        if uricheck(longuri):
            memory[shorturi] = longuri

            self.send_response(303)
            self.send_header("Location","/")

            self.end_headers()
        else:
            self.send_response(404)
            self.send_header("Content-type","text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("Couldn't find {}".format(longuri).encode())


class ThreadHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    "This is an HTTPServer that supports thread-based concurrency."


if __name__ == '__main__':      
    port = int(os.environ.get('PORT', 8000))

    server_addr = ('',port)
    httpob = ThreadHTTPServer(server_addr,Shortner)
    httpob.serve_forever()