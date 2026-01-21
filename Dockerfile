# Используем Python 3.12 (стабильная версия, совместимая с python-telegram-bot 20.7)
FROM python:3.12-slim

# Устанавливаем системные зависимости для matplotlib
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY bot.py config.py database.py ./

# Создаем директорию для базы данных
RUN mkdir -p /app/data

# Устанавливаем переменную окружения для базы данных
ENV DATABASE_NAME=/app/data/sneezes.db

# Запускаем бота
CMD ["python", "bot.py"]
