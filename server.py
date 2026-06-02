import os
from http.server import HTTPServer
# Импортируем ваш класс handler напрямую
from api.export_chat import handler

if __name__ == "__main__":
    # Railway автоматически назначает порт через переменную окружения PORT
    port = int(os.environ.get('PORT', 8080))
    server_address = ('0.0.0.0', port)
    
    # Передаем ваш готовый handler напрямую в HTTPServer без лишних прокси-классов
    httpd = HTTPServer(server_address, handler)
    print(f"Сервер успешно запущен на порту {port}...")
    httpd.serve_forever()
