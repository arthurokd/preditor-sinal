import streamlit as st
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

# --- CONFIGURAÇÃO DA PÁGINA E ESTILO ---
st.set_page_config(page_title="Preditor de Sinal", layout="centered", page_icon="📡")

st.markdown(
    """
    <style>
    body {
        background-image: url('https://upload.wikimedia.org/wikipedia/commons/5/5c/Marca_IFPB.png');
        background-size: contain;
        background-position: top right;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    .footer {
        position: fixed;
        bottom: 10px;
        left: 0;
        right: 0;
        text-align: center;
        font-size: 16px;
        color: #555;
    }
    </style>

    <div style="text-align: center;">
        <h1 style="color: #4CAF50;">📡 Preditor de Sinal</h1>
        <p style="font-size: 18px;">Informe os dados abaixo para prever o valor do sinal:</p>
    </div>

    <div class="footer">
        Projeto viabilizado pelo CNPq, PIBIC e pelo IFPB
    </div>
    """,
    unsafe_allow_html=True
)

# --- FUNÇÕES COM CACHE ---
@st.cache_data
def carregar_dados():
    url = "https://docs.google.com/spreadsheets/d/1HcvCK4XDx3I5U6wkq7ea0v4POH5o-jtD2ZoTB-xbj6E/export?format=csv"
    df = pd.read_csv(url)

    df['COMBINED_FEATURE'] = (
        df['Distância (cm)'] +
        df['Altura (cm)'] +
        df['Potência (mW)']
    ) / 3

    x_numpy = df[['COMBINED_FEATURE']].values
    y_numpy = df[['Campo (dbm)']].values

    scaler_x = StandardScaler()
    scaler_y = StandardScaler()
    x_normalizado = scaler_x.fit_transform(x_numpy)
    y_normalizado = scaler_y.fit_transform(y_numpy)

    return x_normalizado, y_normalizado, scaler_x, scaler_y, df

@st.cache_resource
def treinar_modelo():
    x_normalizado, y_normalizado, scaler_x, scaler_y, df = carregar_dados()

    x = torch.from_numpy(x_normalizado.astype(np.float32))
    y = torch.from_numpy(y_normalizado.astype(np.float32)).view(-1, 1)

    model = nn.Linear(1, 1)
    criterion = nn.MSELoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

    for _ in range(1000):
        y_pred = model(x)
        loss = criterion(y_pred, y)
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

    return model, scaler_x, scaler_y, df

def prever_sinal(distancia, altura, potencia, modelo, scaler_x, scaler_y):
    combined_feature = (distancia + altura + potencia) / 3
    feature_normalizada = scaler_x.transform(np.array([[combined_feature]]))
    input_tensor = torch.from_numpy(feature_normalizada.astype(np.float32))

    with torch.no_grad():
        pred_normalizado = modelo(input_tensor)
        pred_invertido = scaler_y.inverse_transform(pred_normalizado.numpy())
    return pred_invertido[0][0]

# --- CONTROLE DE ESTADO INICIAL ---
if "distancia" not in st.session_state:
    st.session_state.distancia = 0
if "altura" not in st.session_state:
    st.session_state.altura = 0
if "potencia" not in st.session_state:
    st.session_state.potencia = 100
if "nome_predicao" not in st.session_state:
    st.session_state.nome_predicao = ""
if "predicoes_salvas" not in st.session_state:
    st.session_state.predicoes_salvas = {}

# --- INTERFACE ---
st.text_input("Dê um nome para essa predição:", key="nome_predicao")

col1, col2, col3 = st.columns(3)
with col1:
    st.session_state.distancia = st.number_input("Distância (cm)", min_value=0, step=1, format="%d", key="distancia")
with col2:
    st.session_state.altura = st.number_input("Altura (cm)", min_value=0, step=1, format="%d", key="altura")
with col3:
    st.session_state.potencia = st.selectbox("Potência (mW)", [100, 300], key="potencia")

modelo, scaler_x, scaler_y, df = treinar_modelo()

if st.button("🔍 Prever Sinal"):
    if st.session_state.nome_predicao.strip() == "":
        st.warning("Por favor, insira um nome para sua predição.")
    else:
        sinal = prever_sinal(
            st.session_state.distancia,
            st.session_state.altura,
            st.session_state.potencia,
            modelo, scaler_x, scaler_y
        )
        st.success(f"✅ Sinal predito: **{sinal:.3f} dBm**")

        st.session_state.predicoes_salvas[st.session_state.nome_predicao] = {
            "Distância (cm)": st.session_state.distancia,
            "Altura (cm)": st.session_state.altura,
            "Potência (mW)": st.session_state.potencia,
            "Sinal (dBm)": round(sinal, 3)
        }

        # Resetar os campos após a predição
        st.session_state.distancia = 0
        st.session_state.altura = 0
        st.session_state.potencia = 100
        st.session_state.nome_predicao = ""

# --- CONSULTAR PREDIÇÕES ANTERIORES ---
if st.session_state.predicoes_salvas:
    st.markdown("### 📊 Consultar predições anteriores")
    nomes_predicoes = list(st.session_state.predicoes_salvas.keys())
    nome_selecionado = st.selectbox("Selecione uma predição salva:", [""] + nomes_predicoes)

    if nome_selecionado:
        dados = st.session_state.predicoes_salvas[nome_selecionado]
        st.write("#### Dados da predição:")
        st.write(pd.DataFrame([dados]))
