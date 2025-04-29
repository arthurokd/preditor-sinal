import streamlit as st
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

# --- CONFIGURAÇÃO DA PÁGINA E ESTILO ---
st.set_page_config(page_title="Preditor de Sinal", layout="centered", page_icon="📡")

# CSS personalizado: imagem de fundo e rodapé com nomes
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
        Desenvolvido por <strong>Edvaldo</strong> e <strong>Arthur</strong> — IFPB Campus João Pessoa
    </div>
    """,
    unsafe_allow_html=True
)

# --- FUNÇÕES COM CACHE ---
@st.cache_data
def carregar_dados():
    df = pd.read_csv(
        "https://docs.google.com/spreadsheets/d/e/"
        "2PACX-1vR9GhUPG4srpujFlyNaTi9sZ20Vg9XiqI820gLQXvB_Rst3FyMWEwaNxxjGk_Ut2A6gsvKSWdE5z8Kr"
        "/pub?gid=817252977&single=true&output=csv"
    )

    df['COMBINED_FEATURE'] = (
        df['Distância (cm)'] +
        df['Altura (cm)'] +
        df['Potência (w)']
    ) / 3

    x_numpy = df[['COMBINED_FEATURE']].values
    y_numpy = df[['Sinal']].values

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

# --- INTERFACE DE ENTRADA ---
col1, col2, col3 = st.columns(3)
with col1:
    distancia = st.number_input("Distância (cm)", min_value=0.0, step=0.1)
with col2:
    altura = st.number_input("Altura (cm)", min_value=0.0, step=0.1)
with col3:
    potencia = st.number_input("Potência (w)", min_value=0.0, step=0.1)

# --- TREINAMENTO E PREVISÃO ---
modelo, scaler_x, scaler_y, df = treinar_modelo()

if st.button("🔍 Prever Sinal"):
    sinal = prever_sinal(distancia, altura, potencia, modelo, scaler_x, scaler_y)
    st.success(f"✅ Sinal predito: **{sinal:.2f}**")

    # Gráfico de regressão
#    with torch.no_grad():
 #       x_tensor = torch.from_numpy(
  #          scaler_x.transform(df[['COMBINED_FEATURE']].values).astype(np.float32)
   #     )
    #    y_pred = modelo(x_tensor)
     #   y_pred_inv = scaler_y.inverse_transform(y_pred.numpy())
      #  x_inv = df['COMBINED_FEATURE'].values
       # ordem = np.argsort(x_inv)
#
 #       fig, ax = plt.subplots(figsize=(8, 5))
  #      ax.scatter(x_inv, df['Sinal'].values, color='skyblue', label='Dados reais', alpha=0.5)
   #     ax.plot(x_inv[ordem], y_pred_inv[ordem], color='red', label='Reta de Regressão')
    #    ax.set_xlabel("Variável Combinada")
     #   ax.set_ylabel("Sinal")
      #  ax.set_title("Regressão Linear")
       # ax.grid(True)
        #ax.legend()
        #st.pyplot(fig)
