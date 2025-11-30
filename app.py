import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv
import os

# run_pipeline.py dosyasını import et
try:
    import run_pipeline as pipeline
except Exception as e:
    st.error(f"Pipeline import edilemedi: {e}")

load_dotenv()

st.set_page_config(page_title="NBA Player Comparison", layout="wide")

# CSV yükleme fonksiyonu
@st.cache_data
def load_ranked_players():
    path = "data/processed/player_ranked.csv"
    if not os.path.exists(path):
        st.error(f"{path} bulunamadı.")
        return None
    return pd.read_csv(path)

def main():
    st.title("🏀 NBA Oyuncu Karşılaştırma Aracı")

    # Pipeline çalıştırma butonu
    st.sidebar.subheader("⚙️ Pipeline")
    if st.sidebar.button("Pipeline'ı çalıştır"):
        try:
            if hasattr(pipeline, "main"):
                pipeline.main()
                st.success("Pipeline başarıyla çalıştı!")
            else:
                st.warning("run_pipeline.py içinde main() fonksiyonu bulunmuyor.")
        except Exception as e:
            st.error(f"Pipeline çalıştırılamadı: {e}")

    df = load_ranked_players()
    if df is None:
        st.stop()

    players = df["Player"].tolist()

    p1 = st.sidebar.selectbox("Oyuncu 1", players, index=0)
    p2 = st.sidebar.selectbox("Oyuncu 2", players, index=1)

    if st.sidebar.button("Karşılaştır"):
        p1_data = df[df["Player"] == p1].iloc[0]
        p2_data = df[df["Player"] == p2].iloc[0]

        st.subheader("📊 Skor Karşılaştırması")

        scores = ["final_score", "base_score", "lof_score"]

        # Plotly grafiği düzeltildi
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name=p1,
            x=scores,
            y=[p1_data[s] for s in scores],
            marker_color="#1f77b4",
            text=[f"{p1_data[s]:.3f}" for s in scores],
            textposition="auto"
        ))
        fig.add_trace(go.Bar(
            name=p2,
            x=scores,
            y=[p2_data[s] for s in scores],
            marker_color="#ff7f0e",
            text=[f"{p2_data[s]:.3f}" for s in scores],
            textposition="auto"
        ))
        fig.update_layout(
            barmode="group",
            yaxis_title="Skor",
            xaxis_title="Skor Türü",
            title="Skor Karşılaştırması",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📋 Detaylı Karşılaştırma")
        st.dataframe(df[df["Player"].isin([p1, p2])])

if __name__ == "__main__":
    main()
