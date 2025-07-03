import http.server
import socketserver

PORT = 8000

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serveur démarré sur le port {PORT}")
    print(f"Ouvrez votre navigateur à l'adresse: http://localhost:{PORT}")
    httpd.serve_forever() 