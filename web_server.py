import http.server
import socketserver
import webbrowser
import json
import os

class CalendarHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, calendar_keys=None, calendar_values=None, **kwargs):
        self.calendar_keys = calendar_keys
        self.calendar_values = calendar_values
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/calendar_config.json':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # 如果有传入的配置参数，则使用传入的参数
            if self.calendar_keys and self.calendar_values:
                keys = self.calendar_keys.split('|')
                values = self.calendar_values.split('|')
                config = {keys[i]: values[i] for i in range(len(keys)) if i < len(values)}
            else:
                # 否则尝试从配置文件读取
                config = {}
                config_path = './config.json'
                if os.path.exists(config_path):
                    try:
                        with open(config_path, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                    except Exception as e:
                        print(f"读取日历配置文件失败: {str(e)}")
            
            self.wfile.write(json.dumps(config, ensure_ascii=False).encode('utf-8'))
            return
        return super().do_GET()

def start_web_server(port=8080, calendar_keys=None, calendar_values=None):
    
    try:
        Handler = lambda *args, **kwargs: CalendarHandler(*args, calendar_keys=calendar_keys, calendar_values=calendar_values, **kwargs)
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print(f"服务器启动在 http://localhost:{port}")
            webbrowser.open(f"http://localhost:{port}")
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 48:  # 端口被占用
            print(f"端口 {port} 已被占用，尝试使用其他端口")
            start_web_server(port + 1, calendar_keys, calendar_values)
        else:
            raise e

if __name__ == "__main__":
    start_web_server()