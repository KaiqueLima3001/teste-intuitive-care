-- ====================================================================
-- QUERY 1: Top 5 Operadoras com Maior Crescimento Percentual
-- Desafio: Comparar 1º vs Último trimestre, evitando divisão por zero
-- ====================================================================

/*
   TRADE-OFF TÉCNICO:
   Optei por utilizar Common Table Expressions (CTEs) para isolar o primeiro
   e o último trimestre dinamicamente. Isso torna a query resiliente a mudanças
   nas datas dos arquivos.
   
   Tratamento de Exceção: Operadoras com valor inicial 0 são ignoradas para
   evitar erros matemáticos (divisão por zero) ou crescimentos infinitos irreais.
*/

WITH periodos AS (
    SELECT 
        MIN(CONCAT(ano, trimestre)) as periodo_inicio,
        MAX(CONCAT(ano, trimestre)) as periodo_fim
    FROM despesas_consolidadas
),
inicio AS (
    SELECT d.registro_ans, d.razao_social, d.valor_despesas
    FROM despesas_consolidadas d
    JOIN periodos p ON CONCAT(d.ano, d.trimestre) = p.periodo_inicio
    WHERE d.valor_despesas > 0 -- Evitando divisão por zero
),
fim AS (
    SELECT d.registro_ans, d.valor_despesas
    FROM despesas_consolidadas d
    JOIN periodos p ON CONCAT(d.ano, d.trimestre) = p.periodo_fim
)
SELECT 
    i.registro_ans,
    i.razao_social,
    i.valor_despesas AS valor_inicial,
    f.valor_despesas AS valor_final,
    ROUND(((f.valor_despesas - i.valor_despesas) / i.valor_despesas) * 100, 2) AS crescimento_percentual
FROM inicio i
INNER JOIN fim f ON i.registro_ans = f.registro_ans
ORDER BY crescimento_percentual DESC
LIMIT 5;

-- ====================================================================
-- QUERY 2: Distribuição por UF (Top 5) + Média por Operadora
-- Desafio: Calcular total e média na mesma agregação
-- ====================================================================

SELECT 
    uf,
    SUM(valor_despesas) AS total_despesas,
    COUNT(DISTINCT registro_ans) AS qtd_operadoras,
    ROUND(AVG(valor_despesas), 2) AS media_por_operadora
FROM despesas_consolidadas
GROUP BY uf
ORDER BY total_despesas DESC
LIMIT 5;

-- ====================================================================
-- QUERY 3: Operadoras > Média em pelo menos 2 Trimestres
-- Desafio: Lógica de agregação com filtro condicional
-- ====================================================================

/*
   TRADE-OFF TÉCNICO:
   Utilizei Window Functions (AVG() OVER) dentro de uma CTE para calcular
   a média de cada trimestre sem precisar de subqueries repetitivas.
   Isso melhora a performance e a legibilidade.
*/

WITH medias_trimestrais AS (
    SELECT 
        ano,
        trimestre,
        AVG(valor_despesas) as media_geral_trimestre
    FROM despesas_consolidadas
    GROUP BY ano, trimestre
),
performance_operadoras AS (
    SELECT 
        d.registro_ans,
        d.razao_social,
        d.trimestre,
        d.valor_despesas,
        m.media_geral_trimestre,
        CASE WHEN d.valor_despesas > m.media_geral_trimestre THEN 1 ELSE 0 END AS acima_da_media
    FROM despesas_consolidadas d
    JOIN medias_trimestrais m ON d.ano = m.ano AND d.trimestre = m.trimestre
)
SELECT 
    registro_ans,
    razao_social,
    COUNT(*) AS trimestres_analisados,
    SUM(acima_da_media) AS qtd_trimestres_acima_media
FROM performance_operadoras
GROUP BY registro_ans, razao_social
HAVING SUM(acima_da_media) >= 2 -- O filtro "pelo menos 2 trimestres"
ORDER BY qtd_trimestres_acima_media DESC, razao_social ASC;