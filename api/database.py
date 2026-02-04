import mysql.connector
from api.config import Config

def get_connection():
    connection = mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        charset='utf8mb4',      
        use_unicode=True         
    )
    return connection