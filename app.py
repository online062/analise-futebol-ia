
# Sistema de Análise com IA usando SofaScore API (via sofascore-wrapper)

import asyncio
import streamlit as st
from sofascore_wrapper.api import SofascoreAPI
from sofascore_wrapper.search import Search

# IA simples baseada em estatísticas básicas
def gerar_analise(match_data):
    stats = match_data.get("statistics")
    if not stats:
        return ["Dados estatísticos indisponíveis para esta partida."]

    analise = []

    home = stats.get("home")
    away = stats.get("away")

    if home["goals"] > away["goals"]:
        analise.append("Time da casa tem melhor aproveitamento ofensivo.")
    if home["ballPossession"] > 55:
        analise.append("Time da casa domina posse de bola.")
    if home.get("cornerKicks", 0) > 5:
        analise.append("Time da casa gera muitos escanteios.")
    if away["goals"] < 1:
        analise.append("Time visitante tem baixa produção ofensiva.")

    return analise

# Palpites simples com odds
def gerar_palpites(stats):
    palpite_seguro = "Dupla chance: Casa ou Empate"
    palpite_ousado = "Casa vence com over 2.5 gols"
    odd_segura = 1.55
    odd_ousada = 3.2
    return {
        "seguro": palpite_seguro,
        "odd_segura": odd_segura,
        "ousado": palpite_ousado,
        "odd_ousada": odd_ousada
    }

async def buscar_partida(time):
    api = SofascoreAPI()
    search = Search(api, search_string=time)
    resultados = await search.search_all()
    await api.close()
    return resultados

async def pegar_dados_partida(match_id):
    api = SofascoreAPI()
    data = await api.match(match_id)
    await api.close()
    return data

# Streamlit App
def main():
    st.set_page_config("Análise IA SofaScore", layout="centered")
    st.title("⚽ Sistema de Análise com IA (SofaScore)")

    time_input = st.text_input("Digite o nome de um time para buscar partidas:", "Flamengo")
    if st.button("Buscar Jogo"):
        resultados = asyncio.run(buscar_partida(time_input))
        matches = resultados.get("matches", [])

        if not matches:
            st.warning("Nenhuma partida encontrada.")
            return

        partida = matches[0]
        match_id = partida.get("id")
        match_data = asyncio.run(pegar_dados_partida(match_id))

        st.subheader("📊 Estatísticas da Partida")
        stats = match_data.get("statistics", {})
        st.json(stats)

        st.subheader("🤖 Análise da IA")
        analise = gerar_analise(match_data)
        for item in analise:
            st.write("-", item)

        st.subheader("🎯 Palpites")
        palpites = gerar_palpites(stats)
        st.success(f"Seguro ({palpites['odd_segura']}): {palpites['seguro']}")
        st.warning(f"Ousado ({palpites['odd_ousada']}): {palpites['ousado']}")

if __name__ == "__main__":
    main()
