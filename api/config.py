import os

class Config:
    # Configurações do Banco de Dados
    DB_HOST = "localhost"
    DB_USER = "root"
    DB_PASSWORD = "sua_senha"
    DB_NAME = "intuitive_care"
    
    # Configurações do Flask
    DEBUG = True
    SECRET_KEY = os.urandom(24)
    
DEFAULT_PAGE = 1
DEFAULT_LIMIT = 10
MAX_LIMIT = 50