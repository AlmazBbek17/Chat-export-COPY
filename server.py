import os
from http.server import HTTPServer
# Импортируем ваш обработчик из папки api
from api.export_chat import handler 

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    server_address = ('0.0.0.0', port)
    
    httpd = HTTPServer(server_address, handler)
    print(f"Сервер запущен на порту {port} через server.py...")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер остановлен.")
        httpd.server_close()
