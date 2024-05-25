import http.server
import socketserver
import os
import urllib.parse
import mysql.connector
import json

PORT = 8000


# page stuff
class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = 'index.html'
        elif self.path == '/about':
            self.path = '/about.html'
        elif self.path == '/login':
            self.path = '/login.html'
        else:
            # If the requested URL is not found, serve a 404 page
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'404 Not Found x-x')
            return

        # Serve the requested file
        return http.server.SimpleHTTPRequestHandler.do_GET(self)



    def do_POST(self):
        if self.path == '/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = urllib.parse.parse_qs(post_data.decode('utf-8'))

            email = data.get('email', [None])[0]
            password = data.get('password', [None])[0]

            if email and password:
                if self.authenticate_user(email, password):
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'status': 'success', 'message': 'Logged in successfully'}).encode('utf-8'))
                else:
                    self.send_response(401)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'status': 'fail', 'message': 'Invalid credentials'}).encode('utf-8'))
            else:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'fail', 'message': 'Email and Password are required'}).encode('utf-8'))

    # mysql connection
    def authenticate_user(self, email, password):
        conn = mysql.connector.connect(
            host='3306',
            user='root',
            password='root',
            database='juneydb'
        )
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email=%s AND password=%s', (email, password))
        result = cursor.fetchone()
        conn.close()
        return result is not None




# Set the directory to serve files from
directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(directory)

handler = CustomHandler

with socketserver.TCPServer(("", PORT), handler) as httpd:
    print(f"Server running on port {PORT}")
    httpd.serve_forever()
