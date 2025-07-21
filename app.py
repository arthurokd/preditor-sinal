import streamlit as st
import math

st.set_page_config(page_title="Preditor de Sinal", layout="centered")

st.markdown("<h1 style='text-align: center; color: #2c3e50;'>📡 Predição de Sinal (dbm)</h1>", unsafe_allow_html=True)

# Inicializar o dicionário de previsões se não existir
if "previsoes" not in st.session_state:
    st.session_state.previsoes = {}

# Entradas do usuário
st.divider()
st.markdown("### 🔢 Insira os dados abaixo para calcular o sinal:")

titulo = st.text_input("Título da predição")

col1, col2 = st.columns(2)
with col1:
    distancia = st.number_input("Distância (cm)", min_value=0, step=1, format="%d", key="distancia_input")
with col2:
    altura = st.number_input("Altura da Antena (cm)", min_value=0, step=1, format="%d", key="altura_input")

# Função de predição (pode ser substituída pela fórmula real)
def prever_sinal(distancia_cm, altura_cm):
    if distancia_cm == 0:
        return float('-inf')  # Evita log(0)
    sinal = -20 * math.log10(distancia_cm / 100) + 10 * math.log10(altura_cm + 1)
    return sinal

# Botão animado
if st.button("📊 Prever sinal", type="primary"):
    if titulo.strip() == "":
        st.warning("Por favor, insira um título para a predição.")
    else:
        resultado = prever_sinal(distancia, altura)
        st.success(f"📶 Sinal previsto: **{resultado:.3f} dBm**")

        # Salva a predição
        st.session_state.previsoes[titulo] = {
            "Distância (cm)": distancia,
            "Altura (cm)": altura,
            "Sinal (dBm)": round(resultado, 3)
        }

        # Resetar campos
        st.session_state.distancia_input = 0
        st.session_state.altura_input = 0
        st.session_state["titulo"] = ""

# Seleção de predições anteriores
st.divider()
st.markdown("### 📁 Consultar predições anteriores")

if st.session_state.previsoes:
    opcoes = list(st.session_state.previsoes.keys())
    selecao = st.selectbox("Selecione uma predição para visualizar os detalhes", [""] + opcoes)

    if selecao and selecao in st.session_state.previsoes:
        dados = st.session_state.previsoes[selecao]
        st.markdown("#### Detalhes da predição:")
        st.write(f"**Título:** {selecao}")
        st.write(f"**Distância:** {dados['Distância (cm)']} cm")
        st.write(f"**Altura:** {dados['Altura (cm)']} cm")
        st.write(f"**Sinal (dBm):** {dados['Sinal (dBm)']:.3f} dBm")
else:
    st.info("Nenhuma predição foi realizada ainda.")

st.markdown("---")
st.markdown("<small>Projeto viabilizado pelo CNPq, PIBIC e pelo IFPB</small>", unsafe_allow_html=True)
