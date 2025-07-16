import sqlite3
import json
import logging
import os
from datetime import datetime
from typing import Optional, Dict, List
from threading import Lock

logger = logging.getLogger(__name__)

class NumberCache:
    def __init__(self, db_path: str = "numbers.db"):
        self.db_path = db_path
        self.lock = Lock()
        self._init_db()
    
    def _init_db(self):
        """Inicializa la base de datos"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabla simple para números
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS numbers (
                    phone TEXT PRIMARY KEY,
                    name TEXT,
                    data TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
    
    def add_number(self, phone: str, name: str = None, data: Dict = None) -> bool:
        """Agrega o actualiza un número"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                now = datetime.now().isoformat()
                data_str = json.dumps(data) if data else None
                
                cursor.execute('''
                    INSERT OR REPLACE INTO numbers 
                    (phone, name, data, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (phone, name, data_str, now, now))
                
                conn.commit()
                conn.close()
                return True
                
        except Exception as e:
            logger.error(f"Error adding number {phone}: {str(e)}")
            return False
    
    def get_number(self, phone: str) -> Optional[Dict]:
        """Obtiene información de un número"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM numbers WHERE phone = ?', (phone,))
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    result = dict(row)
                    if result['data']:
                        result['data'] = json.loads(result['data'])
                    return result
                return None
                
        except Exception as e:
            logger.error(f"Error getting number {phone}: {str(e)}")
            return None
    
    def get_all_numbers(self) -> List[Dict]:
        """Obtiene todos los números"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM numbers ORDER BY updated_at DESC')
                rows = cursor.fetchall()
                conn.close()
                
                results = []
                for row in rows:
                    result = dict(row)
                    if result['data']:
                        result['data'] = json.loads(result['data'])
                    results.append(result)
                
                return results
                
        except Exception as e:
            logger.error(f"Error getting all numbers: {str(e)}")
            return []
    
    def delete_number(self, phone: str) -> bool:
        """Elimina un número"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM numbers WHERE phone = ?', (phone,))
                conn.commit()
                deleted = cursor.rowcount > 0
                conn.close()
                return deleted
                
        except Exception as e:
            logger.error(f"Error deleting number {phone}: {str(e)}")
            return False
    
    def clear_all(self) -> int:
        """Limpia todos los números"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM numbers')
                conn.commit()
                deleted = cursor.rowcount
                conn.close()
                return deleted
                
        except Exception as e:
            logger.error(f"Error clearing all numbers: {str(e)}")
            return 0

# Instancia global
_cache_instance = None

def get_number_cache() -> NumberCache:
    """Obtiene la instancia del cache de números"""
    global _cache_instance
    if _cache_instance is None:
        db_path = os.getenv('CACHE_DB_PATH', 'numbers.db')
        _cache_instance = NumberCache(db_path)
    return _cache_instance
