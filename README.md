# Teste Técnico - Intuitive Care

Olá! Me chamo **Kaique Lima da Silva**.

Este repositório contém a minha solução para o teste técnico. Como estudante de Ciência da Computação, busquei aplicar boas práticas de desenvolvimento web e processamento de dados.

Esta é a minha primeira documentação técnica oficial, então procurei ser o mais detalhista e transparente possível para facilitar a execução do projeto na sua máquina.

---

## 📂 Estrutura do Projeto

teste-intuitive-care/
│
├── api/ # Backend Flask
├── docs/ # Contem o json do POSTMAN
├── data/ # Dados brutos e tratados
├── frontend/ # Interface Web em Vue.js
├── scripts/ # Scripts ETL
├── sql/ # Scripts SQL
└── requirements.txt # Dependências Python

---

## 🛠️ Tecnologias

* Python 3.12+
* MySQL
* Flask & Flask-CORS
* Pandas
* Vue.js 3 & Chart.js

---

## 🚀 Como Rodar o Projeto

1. **Clonar o Repositório**

    ```bash
    git clone <url-do-repositorio>
    cd teste-intuitive-care
    ```

2. **Criar Ambiente Virtual**

    ```bash
    python -m venv venv
    ```

    Ativar ambiente:

    ```bash
    source venv\Scripts\activate
    ```

3. **Instalar Dependências**

    ```bash
    pip install -r requirements.txt
    ```

4. **Configurar Banco de Dados**
    Configurar o acesso ao MySQL(host, user, password) no arquivo:

    ```bash
    api/config.py e scripts/load_mysql.py
    ```

5. **Baixar os arquivos:**

    ```bash
    python scripts/download_data.py
    ```

6. **Tratar e limpar os dados:**

    ```bash
    python scripts/transform_data.py
    ```

7. **Executar Pipeline de Dados**
    Este processo cria o banco, cria tabelas e importa os dados.

    ```bash
    python scripts/load_mysql.py
    ```

8. **Executar API**
    Na pasta raiz:

    ```bash
    python -m api.app
    ```

9. **Executar Frontend**

    ```bash
    cd frontend
    npm install
    npm run dev
    ```

### 📊 Funcionalidades Implementadas

#### ✔ API

**Listar operadoras com paginação:**

```bash
GET /api/operadoras
```

**Buscar operadora por CNPJ:**

```bash
GET /api/operadoras/{cnpj}
```

**Buscar histórico de despesas:**

```bash
GET /api/operadoras/{cnpj}/despesas
```

**Estatísticas gerais:**

```bash
GET /api/estatisticas
```

**✔ Interface Web:**

*Tabela paginada de operadoras
*Busca por CNPJ ou razão social
*Dashboard com estatísticas
*Gráfico de despesas por UF
*Página de detalhes da operadora

## Trade-offs Técnicos e Decisões de Implementação

Abaixo, respondo às questões de trade-off levantadas no documento do teste:

### 1.2 Processamento em Memória vs Incremental

**Decisão:** Escolhi utilizar a biblioteca Pandas para processar os arquivos em memória (batch).

**Justificativa:** Embora o processamento incremental (stream) economize memória RAM, os arquivos CSV da ANS apresentavam problemas complexos de codificação (**latin-1** misturado com **utf-8**) e inconsistências nos separadores (ponto e vírgula). O Pandas oferece ferramentas mais robustas para tratar e limpar esses erros de uma só vez antes de enviar ao banco. Como o volume de dados para este teste cabia na memória de uma máquina padrão, priorizei a integridade e limpeza dos dados.

### 1.3 Tratamento de Inconsistências nos Dados

Durante a consolidação dos dados, algumas inconsistências foram encontradas e tratadas da seguinte forma:

#### CNPJs duplicados com razões sociais diferentes

Foi realizado agrupamento pelo CNPJ. Para dados cadastrais, mantive o valor mais consistente ou mais frequente. Também foram criados campos auxiliares para indicar possíveis inconsistências.

A decisão de não excluir registros foi tomada para preservar rastreabilidade e permitir análises futuras.

---

#### Valores zerados ou negativos

Os valores foram mantidos conforme estavam na base original. Em contextos financeiros, valores negativos podem representar ajustes ou estornos, portanto removê-los poderia gerar distorções analíticas.

Para garantir controle, criei flags que permitem identificar registros suspeitos.

---

#### Datas e trimestres inconsistentes

Utilizei conversão forçada com `pd.to_datetime(errors='coerce')`. Registros inválidos foram marcados como nulos e posteriormente descartados quando impossibilitavam análise temporal.

Sem a referência temporal, o valor financeiro perde relevância analítica.

---

### 2.1 Tratamento de CNPJs inválidos

**Estratégia adotada:** Sanitização + validação estrutural.

Todos os CNPJs foram normalizados removendo caracteres não numéricos. Após isso, foi validado se o valor possuía 14 dígitos.

Também foram criados campos auxiliares para armazenar o CNPJ limpo e indicar validade.

**Prós:**

* Padroniza chave de relacionamento
* Facilita joins e consultas

**Contras:**

* Possível perda de registros que poderiam ser corrigidos manualmente

Optei por priorizar integridade referencial e consistência do banco.

---

### 2.2 Join entre dados cadastrais e financeiros

**Decisão:** Join realizado durante o processamento dos dados antes da persistência.

Utilizei merge via Pandas para consolidar os dados antes da inserção no banco. Essa abordagem permitiu garantir que apenas dados válidos e consistentes fossem armazenados.

Registros sem correspondência no cadastro foram mantidos, porém marcados como inconsistentes, pois podem ser úteis para auditoria.

Nos casos onde o cadastro apresentava múltiplos registros para o mesmo CNPJ, priorizei o primeiro registro consistente encontrado.

---

### 2.3 Cálculo de estatísticas e ordenação

As métricas de média trimestral e desvio padrão foram calculadas durante a etapa de transformação utilizando agrupamentos do Pandas.

Já a ordenação para consultas analíticas foi delegada ao banco de dados através de `ORDER BY`, pois bancos relacionais possuem otimizações específicas para esse tipo de operação.

---

### 3.2 Normalização do Banco

**Decisão:** Estrutura parcialmente normalizada.

Foram criadas tabelas separadas para:

* Operadoras (dados cadastrais)
* Despesas consolidadas
* Despesas agregadas

Essa abordagem reduz redundância e melhora organização dos dados, ao mesmo tempo em que mantém consultas analíticas eficientes.

Considerando que a tabela de despesas possui volume significativamente maior, a normalização gera economia relevante de armazenamento.

---

### Tipos de Dados

#### Valores monetários

Utilizei `DECIMAL`, evitando `FLOAT`. Dados financeiros exigem precisão absoluta, e floats podem gerar erros de arredondamento.

---

#### Datas

Optei por armazenar Ano e Trimestre separadamente, pois os dados já são fornecidos nesse formato e facilita consultas analíticas.

---

### 3.3 Tratamento de inconsistências na importação

Valores NULL foram mantidos quando não era possível inferir um valor confiável.

Strings em campos numéricos passaram por tentativa de conversão. Quando não era possível converter, o registro era marcado como inválido.

Datas inconsistentes foram padronizadas durante o ETL.

---

### 3.4 Estratégia das Queries Analíticas

#### Crescimento percentual de despesas

Operadoras sem dados completos em todos os trimestres foram consideradas apenas quando havia dados suficientes para cálculo confiável.

---

#### Distribuição por UF

Foi utilizado agrupamento SQL com cálculo tanto do total quanto da média por operadora dentro do estado.

---

#### Operadoras acima da média geral

Utilizei subqueries e CTEs para tornar a consulta mais legível e fácil de manter, evitando lógica complexa no backend.

---

### 4.2.1 Escolha do Framework

**Framework escolhido:** Flask

O Flask foi escolhido por ser um microframework leve, com baixa complexidade e ideal para APIs REST simples. Para o escopo do projeto, ele atendeu perfeitamente aos requisitos, oferecendo flexibilidade e facilidade de manutenção.

Embora o FastAPI ofereça vantagens em performance assíncrona, o ganho seria pouco significativo considerando o uso de consultas SQL síncronas.

---

### 4.2.2 Estratégia de Paginação

**Estratégia escolhida:** Offset-based pagination.

Foi escolhida pela simplicidade de implementação e facilidade de integração com o frontend. Para o volume de dados utilizado no projeto, o impacto de performance é aceitável.

---

### 4.2.3 Estratégia de Estatísticas

**Decisão:** Utilização de dados pré-calculados.

Durante o ETL, foi criada uma tabela agregada contendo métricas estatísticas. A API apenas consulta essa tabela, reduzindo drasticamente o tempo de resposta.

Essa abordagem evita cálculos pesados a cada requisição.

---

### 4.2.4 Estrutura de Resposta da API

Foi adotado o retorno com dados e metadados:

```json
{
  "data": [...],
  "page": 1,
  "limit": 10,
  "total": 100
}
```

Isso facilita a implementação da paginação no frontend e melhora a experiência do usuário.

### 4.3.1 Estratégia de Busca

**Escolha:** Busca no servidor.

Essa abordagem evita sobrecarga no navegador e permite trabalhar com volumes maiores de dados, utilizando o banco para filtrar resultados.

### 4.3.2 Gerenciamento de Estado

**Escolha:** Uso de reatividade do Vue 3 com Props e Events

A aplicação possui complexidade moderada, não exigindo ferramentas. Essa decisão manteve o código mais simples e direto.

### 4.3.3 Performance da Tabela

A performance foi garantida através da paginação no backend, limitando a quantidade de registros renderizados simultaneamente.

### 4.3.4 Tratamento de Erros e Loading

Todas as chamadas assíncronas utilizam **try/catch**.

Estados de loading são controlados por variáveis reativas para exibição de indicadores visuais.

Mensagens de erro são exibidas dentro da interface para não interromper a experiência do usuário. Informações técnicas detalhadas ficam apenas no console para debug.

### 4.4 Documentação da API

Foi criada uma coleção no Postman contendo todas as rotas da API com exemplos completos de requisições e respostas.

**Para utilizar:**

1. Abra o Postman
2. Clique em Import
3. Selecione o arquivo localizado em:

```json
docs/postman/Intuitive Care API.postman_collection.json
```
