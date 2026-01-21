import sqlite3
from datetime import datetime, date
from typing import Optional, List, Tuple
import config


class Database:
    def __init__(self, db_name: str = config.DATABASE_NAME):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        """Создает соединение с базой данных"""
        return sqlite3.connect(self.db_name)
    
    def init_database(self):
        """Инициализирует базу данных и создает таблицу если её нет"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sneezes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, date)
            )
        ''')
        conn.commit()
        conn.close()
    
    def add_sneeze(self, user_id: int, count: int, target_date: Optional[str] = None) -> bool:
        """
        Добавляет или обновляет количество чиханий за день
        
        Args:
            user_id: ID пользователя Telegram
            count: Количество чиханий
            target_date: Дата в формате YYYY-MM-DD (если None, используется сегодня)
        
        Returns:
            True если успешно
        """
        if target_date is None:
            target_date = date.today().isoformat()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO sneezes (user_id, date, count)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, date) DO UPDATE SET count = ?
            ''', (user_id, target_date, count, count))
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении записи: {e}")
            return False
        finally:
            conn.close()
    
    def get_month_stats(self, user_id: int, year: int, month: int) -> List[Tuple[str, int]]:
        """
        Получает статистику за месяц
        
        Args:
            user_id: ID пользователя Telegram
            year: Год
            month: Месяц (1-12)
        
        Returns:
            Список кортежей (дата, количество)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Формируем диапазон дат для месяца
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"
        
        cursor.execute('''
            SELECT date, count
            FROM sneezes
            WHERE user_id = ? AND date >= ? AND date < ?
            ORDER BY date
        ''', (user_id, start_date, end_date))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_period_stats(self, user_id: int, start_date: str, end_date: str) -> List[Tuple[str, int]]:
        """
        Получает статистику за период
        
        Args:
            user_id: ID пользователя Telegram
            start_date: Начальная дата в формате YYYY-MM-DD
            end_date: Конечная дата в формате YYYY-MM-DD (не включая)
        
        Returns:
            Список кортежей (дата, количество)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT date, count
            FROM sneezes
            WHERE user_id = ? AND date >= ? AND date < ?
            ORDER BY date
        ''', (user_id, start_date, end_date))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_week_stats(self, user_id: int, target_date: Optional[str] = None) -> List[Tuple[str, int]]:
        """
        Получает статистику за неделю (7 дней начиная с указанной даты)
        
        Args:
            user_id: ID пользователя Telegram
            target_date: Дата в формате YYYY-MM-DD (если None, используется сегодня)
        
        Returns:
            Список кортежей (дата, количество)
        """
        from datetime import timedelta
        
        if target_date is None:
            target_date = date.today()
        else:
            target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        
        start_date = target_date - timedelta(days=6)  # 7 дней включая сегодня
        end_date = target_date + timedelta(days=1)
        
        return self.get_period_stats(user_id, start_date.isoformat(), end_date.isoformat())
    
    def get_date_count(self, user_id: int, target_date: str) -> Optional[int]:
        """
        Получает количество чиханий за конкретную дату
        
        Args:
            user_id: ID пользователя Telegram
            target_date: Дата в формате YYYY-MM-DD
        
        Returns:
            Количество чиханий или None если записи нет
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT count
            FROM sneezes
            WHERE user_id = ? AND date = ?
        ''', (user_id, target_date))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def update_date_count(self, user_id: int, target_date: str, count: int) -> bool:
        """
        Обновляет количество чиханий за конкретную дату
        
        Args:
            user_id: ID пользователя Telegram
            target_date: Дата в формате YYYY-MM-DD
            count: Новое количество чиханий
        
        Returns:
            True если успешно
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE sneezes
                SET count = ?
                WHERE user_id = ? AND date = ?
            ''', (count, user_id, target_date))
            
            if cursor.rowcount == 0:
                # Если записи нет, создаем новую
                cursor.execute('''
                    INSERT INTO sneezes (user_id, date, count)
                    VALUES (?, ?, ?)
                ''', (user_id, target_date, count))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при обновлении записи: {e}")
            return False
        finally:
            conn.close()
    
    def increment_sneeze(self, user_id: int, target_date: Optional[str] = None) -> Optional[int]:
        """
        Увеличивает количество чиханий на 1 за день
        
        Args:
            user_id: ID пользователя Telegram
            target_date: Дата в формате YYYY-MM-DD (если None, используется сегодня)
        
        Returns:
            Новое количество чиханий или None если ошибка
        """
        if target_date is None:
            target_date = date.today().isoformat()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Сначала пытаемся обновить существующую запись
            cursor.execute('''
                UPDATE sneezes
                SET count = count + 1
                WHERE user_id = ? AND date = ?
            ''', (user_id, target_date))
            
            if cursor.rowcount == 0:
                # Если записи нет, создаем новую с count = 1
                cursor.execute('''
                    INSERT INTO sneezes (user_id, date, count)
                    VALUES (?, ?, 1)
                ''', (user_id, target_date))
            
            # Получаем новое значение
            cursor.execute('''
                SELECT count
                FROM sneezes
                WHERE user_id = ? AND date = ?
            ''', (user_id, target_date))
            
            result = cursor.fetchone()
            conn.commit()
            return result[0] if result else None
        except Exception as e:
            print(f"Ошибка при увеличении счетчика: {e}")
            return None
        finally:
            conn.close()
    
    def get_all_users_stats(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Tuple[int, int]]:
        """
        Получает общую статистику по всем пользователям
        
        Args:
            start_date: Начальная дата в формате YYYY-MM-DD (если None, все записи)
            end_date: Конечная дата в формате YYYY-MM-DD (если None, все записи)
        
        Returns:
            Список кортежей (user_id, общее_количество_чиханий)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if start_date and end_date:
            cursor.execute('''
                SELECT user_id, SUM(count) as total
                FROM sneezes
                WHERE date >= ? AND date < ?
                GROUP BY user_id
                ORDER BY total DESC
            ''', (start_date, end_date))
        else:
            cursor.execute('''
                SELECT user_id, SUM(count) as total
                FROM sneezes
                GROUP BY user_id
                ORDER BY total DESC
            ''')
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_all_users_detailed_stats(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Tuple[int, str, int]]:
        """
        Получает детальную статистику по всем пользователям (по датам)
        
        Args:
            start_date: Начальная дата в формате YYYY-MM-DD (если None, все записи)
            end_date: Конечная дата в формате YYYY-MM-DD (если None, все записи)
        
        Returns:
            Список кортежей (user_id, date, count)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if start_date and end_date:
            cursor.execute('''
                SELECT user_id, date, count
                FROM sneezes
                WHERE date >= ? AND date < ?
                ORDER BY user_id, date
            ''', (start_date, end_date))
        else:
            cursor.execute('''
                SELECT user_id, date, count
                FROM sneezes
                ORDER BY user_id, date
            ''')
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_all_users(self) -> List[int]:
        """
        Получает список всех пользователей
        
        Returns:
            Список user_id
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT user_id
            FROM sneezes
            ORDER BY user_id
        ''')
        
        results = cursor.fetchall()
        conn.close()
        return [row[0] for row in results]