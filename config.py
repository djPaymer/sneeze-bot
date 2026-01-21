import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота из переменной окружения
BOT_TOKEN = os.getenv('BOT_TOKEN', '')

# Название базы данных
DATABASE_NAME = 'sneezes.db'
