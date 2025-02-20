import http.server
import socketserver
import webbrowser

def start_web_server(port=8080):
    Handler = http.server.SimpleHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print(f"服务器启动在 http://localhost:{port}")
            webbrowser.open(f"http://localhost:{port}")
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 48:  # 端口被占用
            print(f"端口 {port} 已被占用，尝试使用其他端口")
            start_web_server(port + 1)
        else:
            raise e

if __name__ == "__main__":
    start_web_server()