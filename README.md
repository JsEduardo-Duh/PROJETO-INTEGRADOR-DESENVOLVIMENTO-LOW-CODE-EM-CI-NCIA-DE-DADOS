# PROJETO-INTEGRADOR-DESENVOLVIMENTO-LOW-CODE-EM-CI-NCIA-DE-DADOS
Projeto Integrador - Ciência de Dados - Grupo 58

Tema do projeto:
Este projeto tem como tema a análise de dados de filmes e séries disponíveis em plataformas de streaming, utilizando o dataset Netflix Movies and TV Shows.

Integrantes:
Fabio Seiji dos Santos
Giovanna Bastos Rodrigues
Jose Eduardo dos Santos Dias Pereira

Objetivo da análise:
O objetivo deste trabalho é analisar os dados de filmes e séries disponíveis na Netflix, com a intenção de entender melhor algumas características do catálogo da plataforma.
A partir disso, buscamos identificar padrões como a quantidade de títulos disponíveis, os gêneros mais comuns, a evolução dos lançamentos ao longo dos anos e a distribuição das produções por país.

Planejamento das tarefas:
As tarefas do projeto foram organizadas entre os integrantes do grupo com o objetivo de facilitar o desenvolvimento do trabalho. Cada etapa foi dividida de acordo com as necessidades do projeto, envolvendo a definição da base de dados, o planejamento do processo ETL (Extract, Transform, Load), a organização do repositório no GitHub e o planejamento das análises e do dashboard. Dessa forma, o grupo consegue trabalhar de maneira mais organizada e eficiente.

Ideia inicial do dashboard:
O dashboard será desenvolvido com o objetivo de apresentar de forma visual os principais resultados da análise. A ideia é criar um painel simples e organizado, com informações como a quantidade de títulos, os gêneros mais frequentes, a evolução dos lançamentos ao longo dos anos e a distribuição das produções por país, facilitando a compreenzsão dos dados.

Planejamento do processo ETL:
- Extração
O processo de ETL para o dataset de títulos da Netflix será estruturado para garantir organização, qualidade e usabilidade dos dados para análises e construção de dashboards. Na etapa de extração, os dados serão obtidos a partir de um arquivo CSV disponibilizado na plataforma Kaggle (https://www.kaggle.com/datasets/shivamb/netflix-shows), contendo informações sobre títulos, tipo de conteúdo, elenco, diretor, país de produção, data de adição ao catálogo, classificação indicativa, duração e gêneros. A extração será realizada com a biblioteca Pandas em Python, carregando os dados em um DataFrame que constituirá a camada bruta (raw).
- Transformação
Durante a transformação, serão aplicados tratamentos para elevar a qualidade e a consistência dos dados. Serão removidos registros duplicados e tratados valores ausentes, substituindo-os por padrões como desconhecido quando necessário. Haverá padronização de campos textuais para garantir uniformidade em atributos como país, elenco e gêneros.
Também serão efetuadas conversões de tipos de dados, por exemplo, transformando a coluna de data de adição para o tipo datetime. A coluna de duração, que apresentará formatos distintos para filmes (minutos) e séries (número de temporadas), será desmembrada em variáveis separadas para permitir análises mais precisas. Serão criadas colunas derivadas, como ano e mês de adição, tempo de permanência no catálogo e categorização do tipo de conteúdo.
Além disso, os campos que contiverem múltiplos valores em uma única célula — como elenco, países e gêneros — serão normalizados e reorganizados em estruturas separadas, favorecendo modelagem relacional e consultas mais confiáveis.
- Carga
Na etapa de carga, os dados tratados serão estruturados para armazenamento em banco de dados ou exportação para ferramentas de visualização. Considerará a adoção de um modelo analítico, como o modelo estrela, com uma tabela fato central contendo os títulos e tabelas dimensão para atributos de tempo, gênero, país e tipo de conteúdo. Alternativamente, os conjuntos poderão ser exportados diretamente para ferramentas de Business Intelligence, como Power BI, possibilitando a criação de dashboards interativos.
