"""Extend Python's built in HTTP server to save files
   Windows upload command example (replace IP and file path as necessary):
   powershell -ep bypass -c "$wc=New-Object Net.WebClient;$wc.UploadFile('http://127.0.0.1:8080/upload.bin', 'PUT', 'c:\\upload.bin');"
"""
import os
import http.server as server

class HTTPRequestHandler(server.SimpleHTTPRequestHandler):
    """Extend SimpleHTTPRequestHandler to handle PUT requests"""
    def do_PUT(self):
        """Save a file following a HTTP PUT request"""
        filename = os.path.basename(self.path)

        # Don't overwrite files
        if os.path.exists(filename):
            self.send_response(409, 'Conflict')
            self.end_headers()
            reply_body = '"%s" already exists\n' % filename
            self.wfile.write(reply_body.encode('utf-8'))
            return

        file_length = int(self.headers['Content-Length'])
        read = 0
        with open(filename, 'wb+') as output_file:
            while read < file_length:
                new_read = self.rfile.read(min(66556, file_length - read))
                read += len(new_read)
                output_file.write(new_read)
        self.send_response(201, 'Created')
        self.end_headers()
        reply_body = 'Saved "%s"\n' % filename
        self.wfile.write(reply_body.encode('utf-8'))
    
    def do_GET(self):
        self.send_response(404, 'Not Found')
        self.end_headers()
        self.wfile.write(b'')


if __name__ == '__main__':
    server.test(HandlerClass=HTTPRequestHandler, port=8080, bind="0.0.0.0")
