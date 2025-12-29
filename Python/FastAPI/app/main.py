
# Импортируем основные компоненты FastAPI
from fastapi import FastAPI
import uvicorn  # ASGI-сервер для запуска приложения
from fastapi.responses import FileResponse

# Создаем экземпляр FastAPI приложения
app = FastAPI()


# Определяем корневой эндпоинт GET-запрос на '/'
@app.get("/")
async def root():
    # Возвращаем JSON-ответ с сообщением
    return FileResponse("index.html")


@app.get("/calculate/")
@app.post("/calculate/")
async def calculate(num1: int, num2: int):
    return {"num1": num1, "num2": num2, "result": num1 + num2}


# Точка входа для запуска приложения
if __name__ == '__main__':
    # Запускаем сервер uvicorn с указанием:
    # - приложения (app)
    # - хоста (127.0.0.1 - локальный сервер)
    # - порта 80 (стандартный HTTP-порт)
    uvicorn.run(app,
                host='127.0.0.1',
                port=80)
