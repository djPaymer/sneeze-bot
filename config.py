import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота из переменной окружения
BOT_TOKEN = os.getenv('BOT_TOKEN', '')

# Название базы данных (можно переопределить через переменную окружения)
DATABASE_NAME = os.getenv('DATABASE_NAME', 'sneezes.db')

# ID администраторов (через запятую, например: "123456789,987654321")
ADMIN_IDS = [int(admin_id.strip()) for admin_id in os.getenv('ADMIN_IDS', '').split(',') if admin_id.strip()]
