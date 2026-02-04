import pandas as pd
import mysql.connector
from pathlib import Path

# ==========================================
# CONFIGURAÇÃO DE MAPEAMENTO (DE -> PARA)
# Chave = Nome no CSV  |  Valor = Nome no Banco
# ==========================================
MAPA_OPERADORAS = {
    "REGISTRO_OPERADORA": "registro_ans",
    "CNPJ":               "cnpj",
    "Razao_Social":       "razao_social",
    "Modalidade":         "modalidade",
    "UF":                 "uf"
}

MAPA_CONSOLIDADO = {
    "CNPJ":                "cnpj",
    "RazaoSocial":         "razao_social",
    "RegistroANS":         "registro_ans",
    "Modalidade":          "modalidade",
    "UF":                  "uf",
    "Ano":                 "ano",
    "Trimestre":           "trimestre",
    "ValorDespesas":       "valor_despesas",
    "razao_social_valida": "razao_social_valida",
    "valor_valido":        "valor_valido",
    "CNPJ_LIMPO":          "cnpj_limpo",
    "cnpj_valido":         "cnpj_valido"
}

MAPA_AGREGADO = {
    "RazaoSocial":     "razao_social",
    "UF":              "uf",
    "TotalDespesas":   "total_despesas",
    "MediaTrimestral": "media_trimestral",
    "DesvioPadrao":    "desvio_padrao"
}

# ==========================
# Configuração do banco
# ==========================
DB_CONFIG_ROOT = {
    "host": "localhost",
    "user": "root",
    "password": "sua_senha",
    "port": 3306,
    "charset": "utf8mb4",
    "use_unicode": True
}

DB_NAME = "intuitive_care"

DB_CONFIG = {
    **DB_CONFIG_ROOT,
    "database": DB_NAME,
}

BASE_DIR = Path(__file__).resolve().parents[1]
DDL_PATH = BASE_DIR / "sql/01_ddl.sql"

ARQUIVOS = {
    "operadoras": BASE_DIR / "data/raw/Relatorio_cadop.csv",
    "consolidado": BASE_DIR / "data/analytics/consolidado_despesas.csv",
    "agregado": BASE_DIR / "data/analytics/despesas_agregadas.csv"
}

# ==========================
# Funções Auxiliares
# ==========================
def get_connection(use_db=True):
    config = DB_CONFIG if use_db else DB_CONFIG_ROOT
    return mysql.connector.connect(**config)

def executar_sql_file(cursor, caminho_sql):
    print(f"Executando script SQL: {caminho_sql}")
    with open(caminho_sql, "r", encoding="utf-8") as f:
        sql_script = f.read()

    comandos = sql_script.split(";")

    for comando in comandos:
        comando = comando.strip()
        if comando:
            cursor.execute(comando)
            
# ==========================
# Função de carregar os csv
# ==========================
def carregar_csv(tabela, arquivo, mapa_colunas, sep=",", encoding="utf-8"):
    print(f"\nCarregando {tabela}...")
    try:
        df = pd.read_csv(arquivo, sep=sep, encoding=encoding)
        
        # Renomear as colunas (De "Razao_Social" para "razao_social")
        df.rename(columns=mapa_colunas, inplace=True)
        
        # Filtrar apenas as colunas que existem no banco
        colunas_finais = list(mapa_colunas.values())
        df = df[colunas_finais]
        
        placeholders = ", ".join(["%s"] * len(colunas_finais))
        colunas_sql = ", ".join([f"`{c}`" for c in colunas_finais])

        sql = f"""
            INSERT INTO `{tabela}` ({colunas_sql})
            VALUES ({placeholders})
        """
        
        df = df.where(pd.notnull(df), None)
        dados = df.to_numpy().tolist()

        conn = get_connection()
        cursor = conn.cursor()
        cursor.executemany(sql, dados)
        conn.commit()

        print(f"{len(dados)} registros inseridos em {tabela}")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao carregar {tabela}: {e}")
    
# ==========================
# EXECUÇÃO PRINCIPAL
# ==========================
if __name__ == "__main__":
    
    # Cria o Database (se não existir)
    print("--- Inicializando Banco de Dados ---")
    conn_root = get_connection(use_db=False)
    cursor_root = conn_root.cursor()
    cursor_root.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    cursor_root.close()
    conn_root.close()

    # Conectando no Banco Oficial
    conn = get_connection(use_db=True)
    cursor = conn.cursor()

    # Criando Tabelas (DDL)
    print("Criando tabelas...")
    executar_sql_file(cursor, DDL_PATH)
    print("Tabelas prontas")

    # Carregar os Arquivos
    
    # Operadoras (Usa utf-8-sig por causa do download_data.py)
    carregar_csv(
        tabela="operadoras",
        arquivo=ARQUIVOS["operadoras"],
        mapa_colunas=MAPA_OPERADORAS,
        sep=";",
        encoding="utf-8-sig"
    )

    # Consolidado
    carregar_csv(
        tabela="despesas_consolidadas",
        arquivo=ARQUIVOS["consolidado"],
        mapa_colunas=MAPA_CONSOLIDADO,
        encoding="utf-8"
    )

    # Agregado
    carregar_csv(
        tabela="despesas_agregadas",
        arquivo=ARQUIVOS["agregado"],
        mapa_colunas=MAPA_AGREGADO,
        encoding="utf-8"
    )
    
    cursor.close()
    conn.close()
    print("\n--- Processo Finalizado com Sucesso ---")