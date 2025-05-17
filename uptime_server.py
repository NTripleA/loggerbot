import os
import threading
import http.server
import socketserver
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# HTTP server configuration
HTTP_PORT = int(os.getenv('HTTP_PORT', 8080))  # Default to port 8080 if not specified

# Custom HTTP request handler
class UptimeHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            # Send a simple OK response for uptime monitoring
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            # Return 404 for all other paths
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    # Suppress console logs for cleaner output
    def log_message(self, format, *args):
        return

# Function to start the HTTP server
def start_http_server():
    handler = UptimeHandler
    httpd = socketserver.TCPServer(("", HTTP_PORT), handler)
    print(f"Starting HTTP server on port {HTTP_PORT}")
    httpd.serve_forever()

# Function to start the HTTP server in a separate thread
def run_server():
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()
    print("HTTP server thread started")
    return http_thread 