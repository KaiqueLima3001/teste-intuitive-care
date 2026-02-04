import requests
from bs4 import BeautifulSoup
import os
import zipfile

URL_BASE = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/"
URL_CADOP = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/"

PASTA_DOWNLOAD  = "data/raw"
PASTA_EXTRAIDA = "data/processed"

def listar_links(url):
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Erro ao acessar a URL: {url}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    links = []
    
    for link in soup.find_all("a"):
        href = link.get("href")
        
        if href and href != "../":
            links.append(href)
            
    return links

def baixar_arquivo(url, nome_arquivo):
    os.makedirs(PASTA_DOWNLOAD , exist_ok=True)   
    caminho = os.path.join(PASTA_DOWNLOAD , nome_arquivo)
    
    response = requests.get(url)
    
    if response.status_code == 200:
        if nome_arquivo.lower().endswith(".zip"):
            with open(caminho, 'wb') as f:
                f.write(response.content)
            print(f"Download concluído: {nome_arquivo}")
        else:
            content = response.content
            texto = None
            try:
                texto = content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    texto = content.decode('cp1252')
                except UnicodeDecodeError:
                    texto = content.decode('latin1')
            
            with open(caminho, 'w', encoding='utf-8-sig') as f:
                f.write(texto)
            print(f"Download e conversão CSV concluídos: {nome_arquivo}")
    else:
        print(f"Erro ao baixar: {nome_arquivo}")

def extrair_zip(nome_arquivo):
    os.makedirs(PASTA_EXTRAIDA, exist_ok=True)
    
    caminho_zip = os.path.join(PASTA_DOWNLOAD , nome_arquivo)
    
    with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
        zip_ref.extractall(PASTA_EXTRAIDA)
    
    print(f"Extração concluída: {nome_arquivo}")
  
if __name__ == "__main__":
    links = listar_links(URL_BASE)
    
    # Fazendo a filtragem e conversão para inteiros dos anos disponíveis    
    anos = [int(link[:-1]) for link in links if link.endswith("/") and link[:-1].isdigit()]
    
    ultimo_ano = max(anos)
    
    url_ano = f"{URL_BASE}{ultimo_ano}/"
    
    links_ano = listar_links(url_ano)

    # Utilizando sorted para ordenar os links dos arquivos .zip
    zips = sorted(
        [link for link in links_ano if link.endswith(".zip")]
    )
    
    ultimos_zips = zips[-3:]
    
    for zip_nome in ultimos_zips:
        url_zip = f"{url_ano}{zip_nome}"
        
        baixar_arquivo(url_zip, zip_nome)
        extrair_zip(zip_nome)
        
    # ==============================
    #! Download do Relatorio CADOP
    # ==============================
    print("Buscando arquivo CADOP...")
    
    links_cadop = listar_links(URL_CADOP)
    
    arquivos_csv = [link for link in links_cadop if link.lower().endswith(".csv")]
    
    if not arquivos_csv:
        raise Exception("Arquivo CADOP não encontrado.")
        
    nome_cadop = arquivos_csv[0]
    url_cadop = f"{URL_CADOP}{nome_cadop}"

    baixar_arquivo(url_cadop, nome_cadop)
    