# ============================================
# PROJETO: Análise de Investimentos B3 + Cripto
# Script: Coleta das ações B3 via Yahoo Finance
# Autor: Gabriel Ramos Cruz
# Período: 2023–2024
# ============================================

import yfinance as yf
import pymysql
import pandas as pd
import numpy as np
import time

# ============================================
# CONFIGURAÇÕES
# ============================================

ANO_INICIO = "2023-01-01"
ANO_FIM = "2025-01-01"

ACOES_B3 = {
    "PETR4": "PETR4.SA",
    "VALE3": "VALE3.SA",
    "ITUB4": "ITUB4.SA",
    "BBDC4": "BBDC4.SA",
    "MGLU3": "MGLU3.SA",
    "AMER3": "AMER3.SA"
}

# ============================================
# CONEXÃO COM MYSQL
# ============================================

conn = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="investimentos",
    charset="utf8mb4"
)

cursor = conn.cursor()

print("=" * 60)
print("📈 COLETA DE AÇÕES B3 — YAHOO FINANCE")
print("=" * 60)
print()

# ============================================
# FUNÇÃO PARA CALCULAR INDICADORES
# ============================================

def calcular_indicadores(df):
    """
    Calcula:
    - retorno diário
    - retorno acumulado
    - volatilidade de 30 dias
    - médias móveis de 7, 30 e 90 dias
    """

    df = df.sort_values("data").copy()

    # Retorno diário em %
    df["retorno_diario"] = df["preco_fechamento"].pct_change() * 100

    # Retorno acumulado em %
    primeiro_preco = df["preco_fechamento"].iloc[0]

    df["retorno_acumulado"] = (
        (df["preco_fechamento"] / primeiro_preco) - 1
    ) * 100

    # Volatilidade móvel de 30 dias
    df["volatilidade_30d"] = (
        df["retorno_diario"]
        .rolling(window=30)
        .std()
    )

    # Médias móveis
    df["media_movel_7d"] = (
        df["preco_fechamento"]
        .rolling(window=7)
        .mean()
    )

    df["media_movel_30d"] = (
        df["preco_fechamento"]
        .rolling(window=30)
        .mean()
    )

    df["media_movel_90d"] = (
        df["preco_fechamento"]
        .rolling(window=90)
        .mean()
    )

    return df


# ============================================
# COLETAR CADA AÇÃO
# ============================================

for ticker_banco, ticker_yahoo in ACOES_B3.items():

    print("-" * 60)
    print(f"🔎 {ticker_banco} → {ticker_yahoo}")

    try:

        # ----------------------------------------
        # Buscar ID do ativo no banco
        # ----------------------------------------

        cursor.execute(
            """
            SELECT ativo_id
            FROM ativos
            WHERE ticker = %s
            """,
            (ticker_banco,)
        )

        resultado = cursor.fetchone()

        if resultado is None:
            print(f"❌ {ticker_banco} não encontrado na tabela ativos.")
            continue

        ativo_id = resultado[0]

        print(f"   ativo_id: {ativo_id}")

        # ----------------------------------------
        # Buscar dados no Yahoo Finance
        # ----------------------------------------

        print("   ⬇️ Baixando dados do Yahoo Finance...")

        acao = yf.Ticker(ticker_yahoo)

        historico = acao.history(
            start=ANO_INICIO,
            end=ANO_FIM,
            auto_adjust=False
        )

        if historico.empty:
            print(f"   ⚠️ Nenhum dado retornado para {ticker_yahoo}")
            continue

        # ----------------------------------------
        # Preparar DataFrame
        # ----------------------------------------

        historico = historico.reset_index()

        historico["data"] = pd.to_datetime(
            historico["Date"]
        ).dt.date

        df = pd.DataFrame({
            "data": historico["data"],
            "preco_abertura": historico["Open"],
            "preco_maximo": historico["High"],
            "preco_minimo": historico["Low"],
            "preco_fechamento": historico["Close"],
            "volume": historico["Volume"]
        })

        # Remover registros inválidos
        df = df.dropna(
            subset=["preco_fechamento"]
        )

        # ----------------------------------------
        # Garantir valores numéricos
        # ----------------------------------------

        colunas_numericas = [
            "preco_abertura",
            "preco_maximo",
            "preco_minimo",
            "preco_fechamento",
            "volume"
        ]

        for coluna in colunas_numericas:
            df[coluna] = pd.to_numeric(
                df[coluna],
                errors="coerce"
            )

        df = df.dropna(
            subset=["preco_fechamento"]
        )

        # ----------------------------------------
        # Variação diária
        # ----------------------------------------

        df["variacao_pct"] = (
            df["preco_fechamento"]
            .pct_change()
            * 100
        )

        print(
            f"   📊 {len(df)} registros encontrados."
        )

        # ========================================
        # INSERIR PREÇOS NO MYSQL
        # ========================================

        inseridos = 0
        existentes = 0

        for _, row in df.iterrows():

            data = row["data"]

            # Verificar se já existe
            cursor.execute(
                """
                SELECT preco_id
                FROM precos_historicos
                WHERE ativo_id = %s
                  AND data = %s
                LIMIT 1
                """,
                (ativo_id, data)
            )

            existe = cursor.fetchone()

            if existe:
                existentes += 1
                continue

            # Converter NaN para None
            def tratar(valor):
                if pd.isna(valor):
                    return None
                return float(valor)

            volume = row["volume"]

            if pd.isna(volume):
                volume = None
            else:
                volume = int(volume)

            cursor.execute(
                """
                INSERT INTO precos_historicos
                (
                    ativo_id,
                    data,
                    preco_abertura,
                    preco_maximo,
                    preco_minimo,
                    preco_fechamento,
                    volume,
                    variacao_pct
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    ativo_id,
                    data,
                    tratar(row["preco_abertura"]),
                    tratar(row["preco_maximo"]),
                    tratar(row["preco_minimo"]),
                    tratar(row["preco_fechamento"]),
                    volume,
                    tratar(row["variacao_pct"])
                )
            )

            inseridos += 1

        conn.commit()

        print(f"   ✅ Novos registros inseridos: {inseridos}")
        print(f"   ℹ️ Registros que já existiam: {existentes}")

        # ========================================
        # CALCULAR INDICADORES
        # ========================================

        print("   📐 Calculando indicadores...")

        df_ind = calcular_indicadores(df)

        indicadores_inseridos = 0

        for _, row in df_ind.iterrows():

            data = row["data"]

            # Verificar se indicador já existe
            cursor.execute(
                """
                SELECT indicador_id
                FROM indicadores
                WHERE ativo_id = %s
                  AND data = %s
                LIMIT 1
                """,
                (ativo_id, data)
            )

            existe = cursor.fetchone()

            if existe:
                continue

            def tratar_ind(valor):
                if pd.isna(valor):
                    return None
                return float(valor)

            cursor.execute(
                """
                INSERT INTO indicadores
                (
                    ativo_id,
                    data,
                    retorno_diario,
                    retorno_acumulado,
                    volatilidade_30d,
                    media_movel_7d,
                    media_movel_30d,
                    media_movel_90d
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    ativo_id,
                    data,
                    tratar_ind(row["retorno_diario"]),
                    tratar_ind(row["retorno_acumulado"]),
                    tratar_ind(row["volatilidade_30d"]),
                    tratar_ind(row["media_movel_7d"]),
                    tratar_ind(row["media_movel_30d"]),
                    tratar_ind(row["media_movel_90d"])
                )
            )

            indicadores_inseridos += 1

        conn.commit()

        print(
            f"   📐 Indicadores inseridos: "
            f"{indicadores_inseridos}"
        )

        print(f"   ✅ {ticker_banco} concluído!")

        time.sleep(2)

    except Exception as erro:

        print(
            f"   ❌ ERRO em {ticker_banco}:"
        )
        print(
            f"      {erro}"
        )

        conn.rollback()


# ============================================
# FINALIZAÇÃO
# ============================================

cursor.close()
conn.close()

print()
print("=" * 60)
print("✅ COLETA B3 FINALIZADA")
print("=" * 60)
print()
print("Agora verifique os registros no MySQL.")