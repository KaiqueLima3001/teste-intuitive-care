from api.database import get_connection

def listar_operadoras(page, limit, search=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    offset = (page - 1) * limit

    query_base = """
        FROM operadoras 
        WHERE 1=1
    """
    params = []
    
    # Implementação da Busca (Trade-off: Busca no Servidor para performance)
    if search:
        query_base += " AND (razao_social LIKE %s OR cnpj LIKE %s)"
        termo = f"%{search}%"
        params.extend([termo, termo])
        
    query_count = f"SELECT COUNT(*) as total {query_base}"
    cursor.execute(query_count, tuple(params))
    total = cursor.fetchone()['total']
    
    query_data = f"""
        SELECT 
            registro_ans as registro,
            cnpj,
            razao_social,
            modalidade,
            uf
        {query_base}
        ORDER BY razao_social
        LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])
    
    cursor.execute(query_data, tuple(params))
    results = cursor.fetchall()
    
    conn.close()
    
    return {
        "data": results,
        "total": total,
        "page": page,
        "limit": limit
    }

def obter_operadora_por_cnpj(cnpj):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            registro_ans as registro,
            cnpj,
            razao_social,
            modalidade,
            uf
        FROM operadoras 
        WHERE cnpj = %s
    """

    cursor.execute(query, (cnpj,))
    result = cursor.fetchone()

    conn.close()
    return result