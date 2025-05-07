import streamlit as st
import requests
import datetime
import time  # Importado para adicionar um tempo de espera antes de limpar a tela

# Credenciais seguras
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

st.title("Chá de Casa Nova 🎁🏠")
st.subheader("Este é um subtítulo")

st.write("Olá! Você está convidado para o nosso chá de casa nova. Por favor, preencha as informações abaixo.")
st.write("A sua presença é muito importante para nós!")
st.write("Agradecemos desde já!")
st.write("Abaixo estão algumas informações sobre o evento.")
st.write("Por favor, preencha seu nome e escolha se irá ao evento.")
st.write("Qualque duvida, entre em contato com a gente!")

# Nome do usuário
nome_usuario = st.text_input("Digite seu nome completo:", key="nome")

# Vai ao evento? Com resposta padrão "Não"
vai_ao_evento = st.radio("Você vai ao chá de casa nova?", ["Sim", "Não"], index=1, key="presenca")

quantidade = 0

# Se o usuário for ao evento, exibe mais informações sobre o evento
if vai_ao_evento == "Sim":
    st.subheader("Detalhes do evento")
    st.write("Local: Av. Dimas Machado, 164 - Chácaras Tubalina e Quartel")
    st.write("Endereço: Residencial Pallace Planalto")
    st.write("Horário: Á definir")
    st.write("Data: Á definir")

if nome_usuario and vai_ao_evento:
    if vai_ao_evento == "Sim":
        # Pergunta quantas pessoas vão
        quantidade = st.number_input("Quantas pessoas no total vão com você? (Ex: você + 2 = 3)", min_value=1, step=1)

        # Buscar produtos disponíveis
        url = f"{SUPABASE_URL}/rest/v1/f_produtos?status=eq.FALSE&select=id,nome_produto,link_produto,preco_medio"
        res = requests.get(url, headers=HEADERS)
        produtos = res.json()
        opcoes = [f"{p['nome_produto']} - R$ {p['preco_medio']:.2f}" for p in produtos]

        if opcoes:
            escolha = st.selectbox("Escolha seu presente:", opcoes)

            item_selecionado = next((p for p in produtos if f"{p['nome_produto']} - R$ {p['preco_medio']:.2f}" == escolha), None)

            if item_selecionado:
                st.markdown(f"[🔗 Ver produto]({item_selecionado['link_produto']})", unsafe_allow_html=True)

        if st.button("Confirmar resposta"):
            # Grava em f_convidados
            payload_convidado = {
                "convidado": nome_usuario,
                "sim_nao": True,
                "quantidade": quantidade
            }
            convidado_url = f"{SUPABASE_URL}/rest/v1/f_convidados"
            res1 = requests.post(convidado_url, headers=HEADERS, json=payload_convidado)

            # Atualiza f_produtos se escolheu item
            if item_selecionado:
                payload_produto = {
                    "user": nome_usuario,
                    "status": True,
                    "data": datetime.datetime.utcnow().isoformat()
                }
                update_url = f"{SUPABASE_URL}/rest/v1/f_produtos?id=eq.{item_selecionado['id']}"
                res2 = requests.patch(update_url, headers=HEADERS, json=payload_produto)
            else:
                res2 = type("Response", (), {"status_code": 204})()  # Dummy sucesso

            if res1.status_code == 201 and res2.status_code == 204:
                st.success("Resposta registrada com sucesso! 🎉")
                time.sleep(2)  # Espera 2 segundos antes de limpar a tela
                st.session_state.clear()  # Limpa todos os dados de sessão (incluindo o nome)
                st.rerun()  # Atualiza a tela
            else:
                st.error(f"Erro ao salvar. Detalhes:\nConvidado: {res1.text}\nProduto: {res2.text if item_selecionado else 'N/A'}")

    else:  # Não vai
        if st.button("Enviar resposta"):
            payload_convidado = {
                "convidado": nome_usuario,
                "sim_nao": False,
                "quantidade": 0
            }
            convidado_url = f"{SUPABASE_URL}/rest/v1/f_convidados"
            res = requests.post(convidado_url, headers=HEADERS, json=payload_convidado)

            if res.status_code == 201:
                st.success("Sua ausência foi registrada com carinho 🥲")
                time.sleep(2)  # Espera 2 segundos antes de limpar a tela
                st.session_state.clear()  # Limpa todos os dados de sessão (incluindo o nome)
                st.rerun()  # Atualiza a tela
            else:
                st.error(f"Erro ao registrar: {res.text}")
else:
    st.warning("Por favor, preencha seu nome e selecione se irá ao evento.")
