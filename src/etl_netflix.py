"""
╔══════════════════════════════════════════════════════════════════════════╗
║        PROJETO INTEGRADOR – Grupo 58                                    ║
║        Ciência de Dados | Centro Universitário Senac                    ║
║                                                                          ║
║        ETL – Netflix Movies and TV Shows                                 ║
║        Dataset: https://www.kaggle.com/datasets/shivamb/netflix-shows   ║
╚══════════════════════════════════════════════════════════════════════════╝

Etapas:
    1. EXTRAÇÃO  – leitura do CSV bruto
    2. TRANSFORMAÇÃO – limpeza, padronização, colunas derivadas, normalização
    3. CARGA     – exportação das tabelas do modelo estrela para CSV

Dependências:
    pip install pandas numpy

Uso:
    python etl_netflix.py

    O script espera o arquivo 'netflix_titles.csv' na mesma pasta.
    Todos os arquivos gerados são salvos em ./output/
"""

import os
import re
import numpy as np
import pandas as pd

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURAÇÕES
# ─────────────────────────────────────────────────────────────────────────────
INPUT_FILE  = "netflix_titles.csv"
OUTPUT_DIR  = "output"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ═════════════════════════════════════════════════════════════════════════════
# 1. EXTRAÇÃO
# ═════════════════════════════════════════════════════════════════════════════
def extrair(caminho: str) -> pd.DataFrame:
    """Lê o CSV bruto e retorna o DataFrame na camada raw."""
    print("\n" + "="*60)
    print("ETAPA 1 – EXTRAÇÃO")
    print("="*60)

    df = pd.read_csv(caminho)

    print(f"  Arquivo carregado : {caminho}")
    print(f"  Linhas            : {len(df):,}")
    print(f"  Colunas           : {list(df.columns)}")
    print(f"\n  Primeiras linhas:")
    print(df.head(3).to_string())

    return df


# ═════════════════════════════════════════════════════════════════════════════
# 2. TRANSFORMAÇÃO
# ═════════════════════════════════════════════════════════════════════════════
def transformar(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    Aplica todas as transformações e retorna um dicionário com as tabelas
    do modelo estrela:
        fato_titulos  – tabela fato central
        dim_genero    – dimensão gênero (normalizada)
        dim_pais      – dimensão país (normalizada)
        dim_elenco    – dimensão elenco (normalizada)
        dim_tempo     – dimensão tempo
        dim_tipo      – dimensão tipo de conteúdo
    """
    print("\n" + "="*60)
    print("ETAPA 2 – TRANSFORMAÇÃO")
    print("="*60)

    df = df.copy()

    # ── 2.1 Remoção de duplicatas ─────────────────────────────────────────
    print("\n  [2.1] Removendo duplicatas...")
    antes = len(df)
    df.drop_duplicates(subset="show_id", inplace=True)
    print(f"        Removidas: {antes - len(df)} | Restantes: {len(df):,}")

    # ── 2.2 Tratamento de valores ausentes ───────────────────────────────
    print("\n  [2.2] Tratando valores ausentes...")
    nulos_antes = df.isnull().sum()

    substituicoes = {
        "director"   : "Desconhecido",
        "cast"       : "Desconhecido",
        "country"    : "Desconhecido",
        "date_added" : "Desconhecido",
        "rating"     : "Desconhecido",
        "duration"   : "Desconhecido",
    }
    df.fillna(substituicoes, inplace=True)
    df["description"] = df["description"].fillna("")

    nulos_depois = df.isnull().sum()
    print("        Nulos tratados por coluna:")
    for col in substituicoes:
        print(f"          {col:<15}: {nulos_antes[col]} → {nulos_depois[col]}")

    # ── 2.3 Padronização de campos textuais ──────────────────────────────
    print("\n  [2.3] Padronizando campos textuais...")
    cols_texto = ["type", "title", "director", "country", "rating", "listed_in"]
    for col in cols_texto:
        df[col] = df[col].astype(str).str.strip()

    df["type"]  = df["type"].str.title()   # "movie" → "Movie"
    df["rating"] = df["rating"].str.upper()

    # ── 2.4 Conversão de data ─────────────────────────────────────────────
    print("\n  [2.4] Convertendo coluna 'date_added' para datetime...")
    df["date_added_clean"] = pd.to_datetime(
        df["date_added"].str.strip(),
        format="%B %d, %Y",
        errors="coerce"          # datas inválidas → NaT
    )
    invalidas = df["date_added_clean"].isna().sum()
    print(f"        Datas convertidas com sucesso: {len(df) - invalidas:,}")
    print(f"        Datas inválidas (NaT)         : {invalidas}")

    # ── 2.5 Colunas derivadas de data ────────────────────────────────────
    print("\n  [2.5] Criando colunas derivadas de data...")
    df["ano_adicao"] = df["date_added_clean"].dt.year.astype("Int64")
    df["mes_adicao"] = df["date_added_clean"].dt.month.astype("Int64")
    df["nome_mes"]   = df["date_added_clean"].dt.strftime("%B")

    # Tempo de permanência no catálogo (em dias até hoje)
    hoje = pd.Timestamp.today().normalize()
    df["dias_no_catalogo"] = (hoje - df["date_added_clean"]).dt.days.astype("Int64")

    print(f"        Colunas criadas: ano_adicao, mes_adicao, nome_mes, dias_no_catalogo")

    # ── 2.6 Separação da coluna 'duration' ───────────────────────────────
    print("\n  [2.6] Separando coluna 'duration'...")

    def extrair_minutos(val):
        m = re.search(r"(\d+)\s*min", str(val))
        return int(m.group(1)) if m else np.nan

    def extrair_temporadas(val):
        m = re.search(r"(\d+)\s*[Ss]eason", str(val))
        return int(m.group(1)) if m else np.nan

    df["duracao_minutos"]    = df.apply(
        lambda r: extrair_minutos(r["duration"]) if r["type"] == "Movie" else np.nan, axis=1)
    df["numero_temporadas"]  = df.apply(
        lambda r: extrair_temporadas(r["duration"]) if r["type"] == "Tv Show" else np.nan, axis=1)

    filmes_com_dur = df[df["type"] == "Movie"]["duracao_minutos"].notna().sum()
    series_com_temp = df[df["type"] == "Tv Show"]["numero_temporadas"].notna().sum()
    print(f"        Filmes com duração (min)  : {filmes_com_dur:,}")
    print(f"        Séries com nº temporadas  : {series_com_temp:,}")

    # ── 2.7 Categorização do tipo de conteúdo ────────────────────────────
    print("\n  [2.7] Criando dimensão tipo de conteúdo...")
    dim_tipo = (
        df[["type"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    dim_tipo.insert(0, "id_tipo", dim_tipo.index + 1)
    df = df.merge(dim_tipo.rename(columns={"type": "type"}), on="type", how="left")

    # ── 2.8 Dimensão Tempo ────────────────────────────────────────────────
    print("\n  [2.8] Criando dimensão tempo...")
    dim_tempo = (
        df[["date_added_clean", "ano_adicao", "mes_adicao", "nome_mes"]]
        .dropna(subset=["date_added_clean"])
        .drop_duplicates(subset=["date_added_clean"])
        .sort_values("date_added_clean")
        .reset_index(drop=True)
    )
    dim_tempo.insert(0, "id_tempo", dim_tempo.index + 1)
    dim_tempo.rename(columns={"date_added_clean": "data"}, inplace=True)
    print(f"        Registros únicos de data: {len(dim_tempo):,}")

    # ── 2.9 Normalização de gêneros (listed_in) ──────────────────────────
    print("\n  [2.9] Normalizando gêneros (listed_in)...")
    generos_exp = (
        df[["show_id", "listed_in"]]
        .assign(genero=df["listed_in"].str.split(", "))
        .explode("genero")
    )
    generos_exp["genero"] = generos_exp["genero"].str.strip()

    generos_unicos = (
        pd.DataFrame({"genero": generos_exp["genero"].unique()})
        .reset_index(drop=True)
    )
    generos_unicos.insert(0, "id_genero", generos_unicos.index + 1)

    dim_genero = generos_unicos.copy()
    fato_titulo_genero = generos_exp.merge(dim_genero, on="genero")[["show_id", "id_genero"]]

    print(f"        Gêneros únicos encontrados: {len(dim_genero)}")
    print(f"        Top 10 gêneros:")
    top_generos = (
        fato_titulo_genero
        .merge(dim_genero, on="id_genero")["genero"]
        .value_counts()
        .head(10)
    )
    for genero, qtd in top_generos.items():
        print(f"          {genero:<35}: {qtd:,}")

    # ── 2.10 Normalização de países ───────────────────────────────────────
    print("\n  [2.10] Normalizando países...")
    paises_exp = (
        df[["show_id", "country"]]
        .assign(pais=df["country"].str.split(", "))
        .explode("pais")
    )
    paises_exp["pais"] = paises_exp["pais"].str.strip()
    paises_exp = paises_exp[paises_exp["pais"] != "Desconhecido"]

    paises_unicos = (
        pd.DataFrame({"pais": paises_exp["pais"].unique()})
        .reset_index(drop=True)
    )
    paises_unicos.insert(0, "id_pais", paises_unicos.index + 1)

    dim_pais = paises_unicos.copy()
    fato_titulo_pais = paises_exp.merge(dim_pais, on="pais")[["show_id", "id_pais"]]

    print(f"        Países únicos encontrados: {len(dim_pais)}")
    print(f"        Top 10 países por produção:")
    top_paises = (
        fato_titulo_pais
        .merge(dim_pais, on="id_pais")["pais"]
        .value_counts()
        .head(10)
    )
    for pais, qtd in top_paises.items():
        print(f"          {pais:<35}: {qtd:,}")

    # ── 2.11 Normalização de elenco ───────────────────────────────────────
    print("\n  [2.11] Normalizando elenco...")
    elenco_exp = (
        df[["show_id", "cast"]]
        .assign(ator=df["cast"].str.split(", "))
        .explode("ator")
    )
    elenco_exp["ator"] = elenco_exp["ator"].str.strip()
    elenco_exp = elenco_exp[elenco_exp["ator"] != "Desconhecido"]

    atores_unicos = (
        pd.DataFrame({"ator": elenco_exp["ator"].unique()})
        .reset_index(drop=True)
    )
    atores_unicos.insert(0, "id_ator", atores_unicos.index + 1)

    dim_elenco = atores_unicos.copy()
    fato_titulo_elenco = elenco_exp.merge(dim_elenco, on="ator")[["show_id", "id_ator"]]

    print(f"        Atores únicos encontrados: {len(dim_elenco):,}")

    # ── 2.12 Tabela fato principal ────────────────────────────────────────
    print("\n  [2.12] Montando tabela fato principal...")
    colunas_fato = [
        "show_id", "id_tipo", "title", "director", "country",
        "date_added_clean", "ano_adicao", "mes_adicao", "nome_mes",
        "dias_no_catalogo", "release_year", "rating",
        "duracao_minutos", "numero_temporadas", "description"
    ]
    fato_titulos = df[colunas_fato].copy()
    fato_titulos.rename(columns={"date_added_clean": "data_adicao"}, inplace=True)
    print(f"        Registros na tabela fato: {len(fato_titulos):,}")

    # ── Estatísticas gerais ───────────────────────────────────────────────
    print("\n" + "-"*60)
    print("  RESUMO ESTATÍSTICO")
    print("-"*60)
    print(f"  Total de títulos        : {len(fato_titulos):,}")
    print(f"  Filmes                  : {(df['type']=='Movie').sum():,}")
    print(f"  Séries (TV Show)        : {(df['type']=='Tv Show').sum():,}")
    print(f"  Ano mais antigo         : {df['release_year'].min()}")
    print(f"  Ano mais recente        : {df['release_year'].max()}")
    duração_media = df[df["type"]=="Movie"]["duracao_minutos"].mean()
    print(f"  Duração média (filmes)  : {duração_media:.0f} min")
    print(f"  Países únicos           : {len(dim_pais)}")
    print(f"  Gêneros únicos          : {len(dim_genero)}")
    print(f"  Atores únicos           : {len(dim_elenco):,}")

    return {
        "fato_titulos"       : fato_titulos,
        "fato_titulo_genero" : fato_titulo_genero,
        "fato_titulo_pais"   : fato_titulo_pais,
        "fato_titulo_elenco" : fato_titulo_elenco,
        "dim_tipo"           : dim_tipo,
        "dim_genero"         : dim_genero,
        "dim_pais"           : dim_pais,
        "dim_elenco"         : dim_elenco,
        "dim_tempo"          : dim_tempo,
    }


# ═════════════════════════════════════════════════════════════════════════════
# 3. CARGA
# ═════════════════════════════════════════════════════════════════════════════
def carregar(tabelas: dict[str, pd.DataFrame], destino: str) -> None:
    """Exporta cada tabela do modelo estrela para um arquivo CSV."""
    print("\n" + "="*60)
    print("ETAPA 3 – CARGA")
    print("="*60)

    for nome, df in tabelas.items():
        caminho = os.path.join(destino, f"{nome}.csv")
        df.to_csv(caminho, index=False, encoding="utf-8-sig")
        print(f"  ✔ {nome:<25} → {caminho}  ({len(df):,} linhas)")

    print(f"\n  Todos os arquivos salvos em: {destino}/")


# ═════════════════════════════════════════════════════════════════════════════
# EXECUÇÃO PRINCIPAL
# ═════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║     ETL – Netflix Movies and TV Shows  |  Grupo 58      ║")
    print("╚══════════════════════════════════════════════════════════╝")

    # Verificar se o arquivo existe
    if not os.path.exists(INPUT_FILE):
        print(f"\n  ATENÇÃO: Arquivo '{INPUT_FILE}' não encontrado.")
        print("  Baixe o dataset em: https://www.kaggle.com/datasets/shivamb/netflix-shows")
        print("  e coloque o arquivo 'netflix_titles.csv' na mesma pasta deste script.\n")
        exit(1)

    # Pipeline ETL
    df_raw    = extrair(INPUT_FILE)
    tabelas   = transformar(df_raw)
    carregar(tabelas, OUTPUT_DIR)

    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║     ETL concluído com sucesso!                          ║")
    print("╚══════════════════════════════════════════════════════════╝\n")
