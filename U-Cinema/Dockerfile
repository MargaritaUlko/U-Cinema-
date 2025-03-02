# Базовый образ Python
FROM python:3.11

# Обновляем пакеты и устанавливаем SQLite
RUN apt-get update && apt-get install -y sqlite3

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта
COPY . .

# Применяем миграции перед запуском сервера
RUN python manage.py migrate

# Открываем порт 8000
EXPOSE 8000

# Запускаем сервер Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
