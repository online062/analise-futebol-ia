
import streamlit as st
import requests

def buscar_time_por_nome(nome_time):
    url = f"https://api.sofascore.com/api/v1/search/{nome_time}"
    res = requests.get(url)
    if res.status_code != 200:
        return None
    dados = res.json()
    times = dados.get("teams", [])
    if not times:
        return None
    return times[0]  # retorna o primeiro time encontrado

def buscar_proximos_jogos(team_id):
    url = f"https://api.sofascore.com/api/v1/team/{team_id}/events/next/0"
    res = requests.get(url)
    if res.status_code != 200:
        return None
    dados = res.json()
    return dados.get("events", [])

def buscar_estatisticas_partida(match_id):
    url = f"https://api.sofascore.com/api/v1/event/{match_id}/statistics"
    res = requests.get(url)
    if res.status_code != 200:
        return None
    return res.json()

def gerar_analise(stats):
    analise = []
    if not stats or "statistics" not in stats:
        return ["Sem dados disponíveis para análise."]
    dados = stats["statistics"]
    for categoria in dados:
        for item in categoria["groups"]:
            for stat in item["statisticsItems"]:
                title = stat["name"]
                home = stat.get("home", 0)
                away = stat.get("away", 0)
                if title == "Ball possession" and home > 60:
                    analise.append("Time da casa domina a posse de bola.")
                if title == "Corner kicks" and home >= 6:
                    analise.append("Time da casa tem muitos escanteios.")
    return list(set(analise))

def gerar_palpites():
    return {
        "seguro": "Dupla chance: Casa ou Empate",
        "odd_segura": 1.60,
        "ousado": "Vitória do time da casa + over 2.5 gols",
        "odd_ousada": 3.10
    }

def main():
    st.set_page_config("Análise Futebol IA", layout="centered")
    st.title("⚽ Análise de Jogos com IA (SofaScore)")

    nome_time = st.text_input("Digite o nome de um time:", "Flamengo")

    if st.button("Buscar Jogos"):
        time = buscar_time_por_nome(nome_time)
        if not time:
            st.warning("Time não encontrado.")
            return

        st.info(f"🔍 Buscando jogos do time: {time['name']}")
        jogos = buscar_proximos_jogos(time["id"])
        if not jogos:
            st.warning("Nenhum jogo futuro encontrado.")
            return

        partida = jogos[0]
        st.subheader(f"🆚 {partida['homeTeam']['name']} vs {partida['awayTeam']['name']}")
        st.write(f"Data: {partida['startDate']}")

        stats = buscar_estatisticas_partida(partida["id"])
        st.subheader("📊 Estatísticas")
        st.json(stats)

        st.subheader("🤖 Análise da IA")
        analise = gerar_analise(stats)
        for linha in analise:
            st.write("- " + linha)

        st.subheader("🎯 Palpites")
        palpites = gerar_palpites()
        st.success(f"Seguro ({palpites['odd_segura']}): {palpites['seguro']}")
        st.warning(f"Ousado ({palpites['odd_ousada']}): {palpites['ousado']}")

if __name__ == "__main__":
    main()
