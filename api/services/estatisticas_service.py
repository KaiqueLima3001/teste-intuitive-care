from api.database import get_connection
from decimal import Decimal

def obter_estatisticas_gerais():
    conn = get_connection()
    
    try:
        # --- CONSULTA 1: TOTAIS ---
        # Abrindo um cursor exclusivo para essa consulta
        cursor1 = conn.cursor(dictionary=True)
        cursor1.execute("""
            SELECT 
                SUM(total_despesas) as total_geral,
                AVG(total_despesas) as media_por_operadora
            FROM despesas_agregadas
        """)
        totais = cursor1.fetchone()
        cursor1.close() # Fechando para limpar a memória
        
        # --- CONSULTA 2: TOP 5 ---
        cursor2 = conn.cursor(dictionary=True)
        cursor2.execute("""
            SELECT 
                razao_social,
                uf,
                total_despesas as total
            FROM despesas_agregadas
            ORDER BY total_despesas DESC
            LIMIT 5
        """)
        top_5 = cursor2.fetchall()
        cursor2.close()
        
        # --- CONSULTA 3: UF ---
        cursor3 = conn.cursor(dictionary=True)
        cursor3.execute("""
            SELECT 
                uf,
                SUM(total_despesas) as total
            FROM despesas_agregadas
            GROUP BY uf
            ORDER BY total DESC
        """)
        distribuicao_uf = cursor3.fetchall()
        cursor3.close()
        
        conn.close()

        # --- CONVERSÃO DE DADOS ---
        def converter(valor):
            if valor is None:
                return 0.0
            if isinstance(valor, Decimal):
                return float(valor)
            return valor

        # Limpeza e Formatação
        uf_limpo = []
        for item in distribuicao_uf:
            uf_limpo.append({
                "uf": item["uf"],
                "total": converter(item["total"])
            })
            
        top5_limpo = []
        for item in top_5:
            top5_limpo.append({
                "razao_social": item["razao_social"],
                "uf": item["uf"],
                "total": converter(item["total"])
            })

        total_geral = converter(totais['total_geral']) if totais else 0.0
        media_geral = converter(totais['media_por_operadora']) if totais else 0.0

        return {
            "total_despesas": total_geral,
            "media_despesas": media_geral,
            "top_5_operadoras": top5_limpo,
            "despesas_por_uf": uf_limpo
        }

    except Exception as e:
        print(f"\n\n>>> ERRO NO PYTHON: {str(e)} <<<\n\n")
        # Se der erro, tenta fechar a conexão para não travar
        try:
            conn.close()
        except:
            pass
        raise e