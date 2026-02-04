from api.database import get_connection

def listar_despesas_por_operadora(cnpj):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            ano,
            trimestre,
            valor_despesas
        FROM despesas_consolidadas
        WHERE cnpj = %s
        ORDER BY ano DESC, trimestre DESC
    """

    cursor.execute(query, (cnpj,))
    results = cursor.fetchall()
    
    conn.close()
    return results