#!/usr/bin/env python3
"""
Custom HTTP Server that serves index.html as the default page
"""
import http.server
import socketserver
import os
from urllib.parse import urlparse

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # If the path is root (/), serve index.html
        if path == '/':
            self.path = '/index.html'
        
        # Call the parent class method to handle the request
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

def run_server(port=8000):
    """Run the HTTP server on the specified port"""
    with socketserver.TCPServer(("", port), CustomHTTPRequestHandler) as httpd:
        print(f"Server running at http://localhost:{port}")
        print(f"Default page: http://localhost:{port}/ (serves index.html)")
        print("Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    run_server()
