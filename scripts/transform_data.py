import pandas as pd
from pathlib import Path
import zipfile
import glob
import os
import re

# ==========================================
# CONFIGURAÇÕES E MAPEAMENTOS
# ==========================================
PASTA_PROCESSED = Path("data/processed")
PASTA_RAW = Path("data/raw")
PASTA_ANALYTICS = Path("data/analytics")

PASTA_ANALYTICS.mkdir(parents=True, exist_ok=True)

# Mapeia variações para um nome padrão
# Isso resolve o problema de arquivos com nomes de colunas diferentes
NORMALIZACAO_COLUNAS = {
    "VL_FINAL": "VL_SALDO_FINAL",
    "VALOR_SALDO_FINAL": "VL_SALDO_FINAL",
    "VL_SALDO_FINAL": "VL_SALDO_FINAL",
    "VALOR": "VL_SALDO_FINAL",
    
    "VL_INICIAL": "VL_SALDO_INICIAL",
    "VALOR_INICIAL": "VL_SALDO_INICIAL",
    "VL_SALDO_INICIAL": "VL_SALDO_INICIAL",
    
    "DESC": "DESCRICAO",
    "DS_CONTA": "DESCRICAO",
    "DESCRICAO": "DESCRICAO",
    
    "REG_ANS": "REG_ANS",
    "REGISTRO_ANS": "REG_ANS",
    "CD_OPERADORA": "REG_ANS"
}

# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================
def validar_cnpj(cnpj: str) -> bool:
    """Valida CNPJ verificando dígitos verificadores."""
    if not cnpj or len(cnpj) != 14 or len(set(cnpj)) == 1:
        return False

    def calcular_digito(cnpj_parcial, pesos):
        soma = sum(int(d) * p for d, p in zip(cnpj_parcial, pesos))
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)

    pesos1 = [5,4,3,2,9,8,7,6,5,4,3,2]
    pesos2 = [6] + pesos1

    dig1 = calcular_digito(cnpj[:12], pesos1)
    dig2 = calcular_digito(cnpj[:12] + dig1, pesos2)

    return cnpj[-2:] == dig1 + dig2

def ler_arquivo_resiliente(caminho_arquivo):
    """
    Tenta ler CSV detectando automaticamente encoding e separador.
    Necessário pois a ANS mistura formatos (UTF-8/Latin-1 e ;/,).
    """
    encodings = ['utf-8', 'latin-1', 'cp1252']
    separadores = [';', ',']
    
    for enc in encodings:
        for sep in separadores:
            try:
                # Lê apenas as primeiras linhas para testar o formato
                df_teste = pd.read_csv(caminho_arquivo, sep=sep, encoding=enc, nrows=5)
                
                # Se leu apenas 1 coluna, provavelmente o separador está errado
                if len(df_teste.columns) > 1:
                    # Se deu certo, lê o arquivo inteiro
                    return pd.read_csv(caminho_arquivo, sep=sep, encoding=enc)
            except:
                continue
                
    raise ValueError(f"Não foi possível ler o arquivo {caminho_arquivo} com os formatos padrões.")

def normalizar_dataframe(df):
    """
    Padroniza nomes de colunas para maiúsculo e aplica o dicionário de sinônimos.
    """
    # 1. Coloca tudo em maiúsculo e remove espaços extras
    df.columns = [c.strip().upper() for c in df.columns]
    
    # 2. Renomeia usando o mapa (se encontrar correspondência)
    # Usa o get para manter o nome original se não estiver no mapa, mas prefere o normalizado
    novas_colunas = {}
    for col in df.columns:
        if col in NORMALIZACAO_COLUNAS:
            novas_colunas[col] = NORMALIZACAO_COLUNAS[col]
            
    df.rename(columns=novas_colunas, inplace=True)
    return df

# ==========================================
# EXECUÇÃO PRINCIPAL
# ==========================================
print("--- Iniciando Processamento (ETL) ---")

# 1. Carregar Arquivos Financeiros (Trimestres)
arquivos = list(PASTA_PROCESSED.glob("*.csv"))
if not arquivos:
    # Tenta buscar na raiz ou subpastas se não achar direto
    arquivos = list(PASTA_PROCESSED.rglob("*.csv"))
    
print(f"Arquivos encontrados: {len(arquivos)}")

dfs = []
for arquivo in arquivos:
    try:
        print(f"Lendo: {arquivo.name}")
        df = ler_arquivo_resiliente(arquivo)
        df = normalizar_dataframe(df)
        
        if "VL_SALDO_FINAL" in df.columns and "DESCRICAO" in df.columns:
            dfs.append(df)
        else:
            print(f"Arquivo {arquivo.name} ignorado: Colunas esperadas não encontradas.")
    except Exception as e:
        print(f"Erro ao processar {arquivo.name}: {e}")
        
if not dfs:
    raise Exception("Nenhum dado válido carregado. Verifique a pasta 'processed'.")

df_final = pd.concat(dfs, ignore_index=True)  

# print("Normalizando valores e datas...")

# Limpeza de Valores Monetários (Remove ponto de milhar, troca vírgula por ponto)
colunas_valores = ["VL_SALDO_INICIAL", "VL_SALDO_FINAL"]
for coluna in colunas_valores:
    if coluna in df_final.columns:
        # Garante que é string antes de replace
        if df_final[coluna].dtype == 'object':
            df_final[coluna] = (
                df_final[coluna]
                .astype(str)
                .str.replace(".", "", regex=False)
                .str.replace(",", ".", regex=False)
            )
        df_final[coluna] = pd.to_numeric(df_final[coluna], errors="coerce").fillna(0.0)

regex_filtro = r"^DESPESAS?\s+COM\s+EVENTOS?/?\s*SINISTROS?"

df_eventos = df_final[
    df_final["DESCRICAO"]
    .astype(str)
    .str.strip()
    .str.upper()
    .str.contains(regex_filtro, regex=True)
].copy()

print(f"Registros filtrados: {len(df_eventos)}")

df_eventos["DATA"] = pd.to_datetime(df_eventos["DATA"], errors="coerce")
df_eventos["Ano"] = df_eventos["DATA"].dt.year
df_eventos["Trimestre"] = df_eventos["DATA"].dt.quarter.apply(lambda x: f"{x}º Trimestre")

# print("Realizando Join com dados cadastrais...")

caminho_cadop = PASTA_RAW / "Relatorio_cadop.csv"
cadop = pd.read_csv(caminho_cadop, sep=";", encoding="utf-8-sig", dtype=str) # Lê tudo como texto para evitar erro

# Normaliza nomes do CADOP
cadop.rename(columns={
    "REGISTRO_OPERADORA": "RegistroANS",
    "Razao_Social": "RazaoSocial"
}, inplace=True)

# Limpa CNPJ
cadop["CNPJ"] = cadop["CNPJ"].str.replace(r"\D", "", regex=True).str.zfill(14)
cadop = cadop[["CNPJ", "RegistroANS", "RazaoSocial", "Modalidade", "UF"]].drop_duplicates("CNPJ")

df_eventos["REG_ANS_JOIN"] = df_eventos["REG_ANS"].astype(str).str.replace(r"\.0$", "", regex=True)
cadop["RegistroANS_JOIN"] = cadop["RegistroANS"].astype(str).str.replace(r"\.0$", "", regex=True)

df_consolidado = df_eventos.merge(
    cadop,
    left_on="REG_ANS_JOIN",
    right_on="RegistroANS_JOIN",
    how="left"
)

# 4. Agregação Final e Validações
print("Consolidando dados...")

df_consolidado = (
    df_consolidado
    .groupby(["CNPJ", "RazaoSocial", "RegistroANS", "Modalidade", "UF", "Ano", "Trimestre"], as_index=False)
    ["VL_SALDO_FINAL"]
    .sum()
)
df_consolidado.rename(columns={"VL_SALDO_FINAL": "ValorDespesas"}, inplace=True)

# Validações solicitadas (Flags)
df_consolidado["razao_social_valida"] = df_consolidado["RazaoSocial"].notna() & (df_consolidado["RazaoSocial"] != "")
df_consolidado["valor_valido"] = df_consolidado["ValorDespesas"] > 0
df_consolidado["CNPJ_LIMPO"] = df_consolidado["CNPJ"].fillna("").astype(str).str.zfill(14)
df_consolidado["cnpj_valido"] = df_consolidado["CNPJ_LIMPO"].apply(validar_cnpj)

# Salvar Arquivos
print("Salvando resultados...")

# CSV Consolidado
output_csv = PASTA_ANALYTICS / "consolidado_despesas.csv"
df_consolidado.to_csv(output_csv, index=False, encoding="utf-8")

with zipfile.ZipFile(str(output_csv).replace(".csv", ".zip"), "w") as zipf:
    zipf.write(output_csv, arcname="consolidado_despesas.csv")

# CSV Agregado (Desafio Extra)
df_agregado = (
    df_consolidado
    .groupby(["RazaoSocial", "UF"], as_index=False)
    .agg(
        TotalDespesas=("ValorDespesas", "sum"),
        MediaTrimestral=("ValorDespesas", "mean"),
        DesvioPadrao=("ValorDespesas", "std")
    )
    .sort_values("TotalDespesas", ascending=False)
)
df_agregado = df_agregado.round(2).fillna(0)

output_agregado = PASTA_ANALYTICS / "despesas_agregadas.csv"
df_agregado.to_csv(output_agregado, index=False, encoding="utf-8")

# Zip final do candidato
with zipfile.ZipFile(PASTA_ANALYTICS / "Teste_Kaique_Lima.zip", "w") as zipf:
    zipf.write(output_agregado, arcname="despesas_agregadas.csv")

print("Processamento concluído com sucesso!")