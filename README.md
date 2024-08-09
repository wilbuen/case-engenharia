# Wilian Bueno

# 🏢 Case de Engenharia de Dados: Construção de uma Arquitetura Lake House

## 📚 Visão Geral

Este projeto faz parte de um case de engenharia de dados que foca na construção de uma **Arquitetura Lake House**. A arquitetura abrange todas as etapas, desde a ingestão até a transformação e exposição dos dados, garantindo escalabilidade e eficiência no processamento de grandes volumes de informações.

## 📂 Estrutura do Projeto

O projeto é organizado em quatro etapas principais:

### 1. **Ingestão de Dados (Foi usado de um diretorio no projeto para simular o s3, se fosse ser implementado o s3, seria usado do boto3 para a integração com a aws).**
   - **Fontes de Dados PostgreSQL:** Incluem `condomínios`, `moradores`, `imóveis` e `transações`.
   - **Ingestão Inicial:** Os dados são extraídos em tempo real de um banco de dados PostgreSQL utilizando **Debezium** e **Kafka**, com checkpoints implementados para garantir tolerância a falhas. A ingestão é simulada utilizando diretórios locais que funcionam como um bucket S3. Esses dados são armazenados na camada **raw** do Data Lake, no formato **Parquet**. Um script em Python e PySpark é utilizado para processar os dados dos tópicos do Kafka e armazená-los na camada **raw**.

### 2. **Transformação de Dados**
   - **Transformação Inicial:** Os dados brutos, que incluem diferentes formatos de datas e valores decimais, são normalizados na camada de transformação. A transformação dinâmica é aplicada a campos que contenham as palavras 'data' ou 'valor' nas colunas, lidando com criptografias e outros ajustes necessários.
   - **Transformação Refinada:** Após a normalização, os dados são refinados para gerar insights valiosos para o time de negócios, com os resultados sendo armazenados na camada **refined** do Data Lake.

### 3. **Processamento de Dados**
   - **Pipelines de Streaming:** Implementação de pipelines de processamento contínuo utilizando **Spark Structured Streaming**, garantindo a ingestão e processamento de dados em tempo real.
   - **Testes Automatizados:** Foram desenvolvidos testes automatizados utilizando **pytest** para verificar e validar todas as etapas do pipeline, assegurando que o processo funcione conforme o esperado.

### 4. **Execução e Testes**
   - **Ambiente Docker:** Todo o processo ocorre em um ambiente Docker, que inclui 5 containers para serviços como Kafka e PostgreSQL. Para iniciar o ambiente Docker, execute os comandos:
     ```bash
     docker-compose build
     docker-compose up -d
     ```
   - **Criação de Conectores:** Para criar os conectores e tópicos no Kafka, execute o seguinte script de teste:
     ```bash
     pytest tests/test_0_create_conector_postg_for_kafka.py
     ```
     Este script verifica a conexão com o Debezium e cria os tópicos necessários para monitorar as tabelas do PostgreSQL. O script de teste já inclui uma requisição mockada.

     Com os tópicos criados, inicie o streaming dos dados executando:
     ```bash
     python3 extract_with_streaming.py
     ```
     Este comando fará a ingestão dos dados existentes no banco de dados para a camada **raw**.

   - **Teste de Ingestão de Dados em Streaming:** 
     Abra um novo terminal e execute o próximo teste, que insere dados no PostgreSQL e permite observar a ingestão em tempo real:
     ```bash
     pytest tests/test_1_insert_data_to_postgres.py
     ```
     Será possível acompanhar a criação dos dados no banco e ver os arquivos Parquet sendo gerados no diretório `datalake/raw/nometabelas`.

   - **Transformação de Dados:**
     Execute o teste do pipeline de transformação:
     ```bash
     pytest tests/test_2_pipeline.py
     ```

## 🛠 Tecnologias Utilizadas

- **Apache Spark** para processamento de dados.
- **Kafka & Debezium** para streaming de dados.
- **PostgreSQL** como banco de dados de origem.
- **Docker** para containerização do ambiente.
- **pytest** para testes automatizados.
- **Python** como linguagem de programação principal.


## 📝 Como seria feita a documentação do design e a implementação da arquitetura e dos pipelines:


### 📄 1. **Documentação do Design da Arquitetura**

#### **1.1. Visão Geral da Arquitetura**
- **Diagrama de Arquitetura:** Incluir um diagrama de arquitetura que ilustre as principais camadas do sistema (ingestão, processamento, transformação, armazenamento e exposição), detalhando como os dados fluem desde a fonte até a camada refinada(Que deve ir ate dataViz, ali foi simulada a entrega na ponta usando um diretorio no projeto).
- **Componentes e Funções:** Descrever cada componente (Kafka, Debezium, Spark, etc.) e sua função dentro da arquitetura, explicando como eles interagem entre si para garantir o fluxo de dados.

#### **1.2. Camadas de Armazenamento**
- **Camada Raw:** Documentar o formato dos dados na camada bruta (ex: Parquet) e a estrutura dos diretórios no Data Lake. Definindo como os arquivos deveriam estar aqui, que no caso, é sem necessidade de tratamento.
- **Camada Transform:** Explicar o processo de normalização e transformação dos dados, incluindo as regras aplicadas para lidar com diferentes formatos de datas e valores. Também, disponibilizar dicionario de como é padronizada essa normalização, para futuros integrantes no time poderem replicar com facilidade o padrão.
- **Camada Refined:** Descrever como os dados são refinados e preparados para análise, incluindo exemplos de queries ou scripts utilizados para gerar os insights.

#### **1.3. Processos de Ingestão e Transformação**
- **Ingestão de Dados:** Detalhar o processo de ingestão de dados em tempo real, explicando o papel do Debezium e Kafka, e como os dados são armazenados no Data Lake. (Importante resaltar que no estado atual do projeto, não estamos identificando o tipo de operação feita no banco, para podermos fazer uma logica para os delete e update nos dados, ou seja, com mais tempo, seria feita essa identificação e divido os dados em diretorios diferentes, para termos esses logs claros dentro da camda raw, posteriomente, unificando eles a partir de logica e tratamento, dentro da camada de transform)
- **Pipelines de Transformação:** Explicar as transformações aplicadas aos dados e os motivos dessas transformações. Incluir pseudocódigo ou exemplos de scripts que ilustram o processo.

### 🛠 **2. Documentação dos Pipelines**

#### **2.1. Descrição dos Pipelines(Não foi implementado Airflow, por conta de maquina, mas uma das sugestões para orquestração da camada de transform adiante para o projeto atual, e a implementação do airflow para coletar os dados da raw de forma periodica)**
- **Pipeline de Ingestão:** Documentar o funcionamento do pipeline de ingestão, desde a configuração inicial até o processamento dos dados em tempo real. Incluir exemplos de configuração do Debezium e tópicos Kafka.
- **Pipeline de Transformação:** Detalhar como os dados são processados e transformados, mencionando quaisquer operações complexas, como a normalização de datas e valores.

#### **2.2. Testes Automatizados**
- **Estrutura de Testes:** Descrever a estrutura de testes criada com `pytest`, incluindo a organização dos arquivos de testes e o propósito de cada conjunto de testes (ex: testes de ingestão, testes de transformação).
- **Exemplos de Testes:** Fornecer exemplos de como os testes foram implementados, explicando o que cada teste verifica e como ele contribui para a garantia de qualidade do pipeline.

### 📊 **3. Monitoramento e Manutenção**

#### **3.1. Estratégia de Monitoramento (Nenhum monitoramento organizado foi implementado, portanto, aqui vamos discorrer sobre possibilidades)**
- **Logs e Métricas:** Descrever como o monitoramento é realizado, incluindo a coleta de logs, métricas e alertas. Se ferramentas específicas de monitoramento (ex: Prometheus, Grafana) forem utilizadas, detalhar como elas estão configuradas.
- **Falhas e Recuperação:** Explicar como o sistema lida com falhas e como a tolerância a falhas é implementada. Incluir exemplos de situações comuns e como elas são resolvidas.

#### **3.2. Manutenção**
- **Atualização de Pipelines:** Instruções sobre como atualizar ou modificar os pipelines existentes, incluindo etapas de validação e teste antes da implementação.
- **Escalabilidade:** Documentar como a arquitetura pode ser escalada para lidar com maiores volumes de dados, incluindo recomendações para ajustes de configuração em cada componente.

### 🎓 **4. Documentação de Usuário**

#### **4.1. Guia de Uso**
- **Execução de Pipelines:** Fornecer um guia passo a passo para executar os pipelines de ingestão e transformação, desde a inicialização do Docker até a execução dos scripts.
- **Guia de Testes:** Explicar como rodar os testes automatizados, o que esperar como resultado e como interpretar os logs de saída.
