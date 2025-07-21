import streamlit as st
import math

# Função para prever o sinal
def prever_sinal(distancia, altura, potencia_mw):
    potencia_dbm = 10 * math.log10(potencia_mw)
    perda = 20 * math.log10(distancia / 100) + 20 * math.log10(2.4e9) - 147.55
    sinal_recebido = potencia_dbm - perda - (altura * 0.1)
    return sinal_recebido

# Inicializa o estado das previsões
if "previsoes" not in st.session_state:
    st.session_state.previsoes = {}

# Define valores padrões para reset
valor_padrao_distancia = 0
valor_padrao_altura = 0
valor_padrao_potencia = "100"
valor_padrao_titulo = ""

# Recupera valores atuais do estado ou define os padrões
if "distancia_input" not in st.session_state:
    st.session_state.distancia_input = valor_padrao_distancia
if "altura_input" not in st.session_state:
    st.session_state.altura_input = valor_padrao_altura
if "potencia_input" not in st.session_state:
    st.session_state.potencia_input = valor_padrao_potencia
if "titulo_input" not in st.session_state:
    st.session_state.titulo_input = valor_padrao_titulo

# Interface
st.markdown("<h1 style='color:green; font-size: 42px;'>Preditor de Sinal</h1>", unsafe_allow_html=True)

st.session_state.distancia_input = st.number_input("Distância (cm)", min_value=1, step=1, value=st.session_state.distancia_input, key="distancia")
st.session_state.altura_input = st.number_input("Altura (cm)", min_value=0, step=1, value=st.session_state.altura_input, key="altura")
st.session_state.potencia_input = st.selectbox("Potência do Roteador", options=["100", "300"], index=["100", "300"].index(st.session_state.potencia_input), key="potencia")
st.session_state.titulo_input = st.text_input("Título da Previsão", value=st.session_state.titulo_input, key="titulo")

# Conversão dos valores
potencia_mw = int(st.session_state.potencia_input)
distancia = st.session_state.distancia_input
altura = st.session_state.altura_input
titulo = st.session_state.titulo_input

if st.button("Prever sinal", type="primary"):
    if titulo.strip() == "":
        st.warning("Por favor, insira um título para a predição.")
    else:
        resultado = prever_sinal(distancia, altura, potencia_mw)
        st.success(f"\U0001F4F6 Sinal previsto: **{resultado:.3f} dBm**")

        st.session_state.previsoes[titulo] = {
            "Distância (cm)": distancia,
            "Altura (cm)": altura,
            "Potência (mW)": potencia_mw,
            "Sinal (dBm)": round(resultado, 3)
        }

        # Resetar campos
        st.session_state.distancia = valor_padrao_distancia
        st.session_state.altura = valor_padrao_altura
        st.session_state.potencia = valor_padrao_potencia
        st.session_state.titulo = valor_padrao_titulo

        st.experimental_rerun()

# Histórico
if st.session_state.previsoes:
    st.markdown("---")
    st.subheader("Histórico de Previsões")
    for titulo, dados in st.session_state.previsoes.items():
        st.markdown(f"### {titulo}")
        st.write(dados)
