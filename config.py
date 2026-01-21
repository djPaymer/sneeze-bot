import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота из переменной окружения
BOT_TOKEN = os.getenv('BOT_TOKEN', '')

# Название базы данных (можно переопределить через переменную окружения)
DATABASE_NAME = os.getenv('DATABASE_NAME', 'sneezes.db')
