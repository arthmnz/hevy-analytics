import pandas as pd
import re
import streamlit as st
import plotly.express as px

df = pd.read_csv("data/workouts.csv")

df = df.drop(columns=["superset_id", "description", "exercise_notes", "rpe"])

meses_pt = {
    "jan": "01", "fev": "02", "mar": "03", "abr": "04",
    "mai": "05", "jun": "06", "jul": "07", "ago": "08",
    "set": "09", "out": "10", "nov": "11", "dez": "12",
}

def converter_data_hevy(coluna):
    extraido = coluna.str.extract(r"(\d+) de (\w+)\. de (\d+), (\d+):(\d+)")
    extraido.columns = ["dia", "mes", "ano", "hora", "minuto"]
    mes_numero = extraido["mes"].map(meses_pt)
    data_texto = (
        extraido["ano"] + "-" + mes_numero + "-" + extraido["dia"].str.zfill(2)
        + " " + extraido["hora"] + ":" + extraido["minuto"]
    )
    return pd.to_datetime(data_texto, format="%Y-%m-%d %H:%M")

df["start_time"] = converter_data_hevy(df["start_time"])
df["end_time"] = converter_data_hevy(df["end_time"])

df_treino = df[df["set_type"] != "warmup"].copy()

df_treino["weight_kg"] = df_treino["weight_kg"].fillna(0)

df_treino["volume"] = df_treino["weight_kg"] * df_treino["reps"]

volume_por_treino = df_treino.groupby(["title", "start_time"])["volume"].sum().reset_index()

volume_por_treino = volume_por_treino.sort_values("start_time")

evolucao_carga = df_treino.groupby(["exercise_title", "start_time"])["weight_kg"].max().reset_index()

evolucao_carga = evolucao_carga.sort_values(["exercise_title", "start_time"])

print(volume_por_treino.head(10))
print(evolucao_carga.head(15))

st.title("Hevy Analytics")

st.write("Volume total por treino (tabela)")

st.dataframe(volume_por_treino)

fig_volume = px.line(
    volume_por_treino,
    x="start_time",
    y="volume",
    title="Volume total do treino",
    markers=True,
)

st.subheader("Evolução da carga por exercício")

exercicios_disponiveis = sorted(evolucao_carga["exercise_title"].unique())
exercicio_escolhido = st.selectbox("Escolha um exercício", exercicios_disponiveis)

dados_exercicio = evolucao_carga[evolucao_carga["exercise_title"] == exercicio_escolhido]

fig_carga = px.line(
    dados_exercicio,
    x="start_time",
    y="weight_kg",
    title=f"Evolução de carga - {exercicio_escolhido}",
    markers=True,
)

col1, col2 = st.columns(2, gap="xlarge")

with col1:
    st.plotly_chart(fig_volume)

with col2:
    st.plotly_chart(fig_carga)