import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv
import os

# Pipeline'dan fonksiyon içe aktar
# pipeline.py içinde bir main(), load_data() veya kendi fonksiyonun varsa onu çağırabilirsin
try:
    import pipeline
except Exception as e:
    st.error(f"Pipeline import edilemedi: {e}")

load_dotenv()

st.set_page_config(page_title="NBA Player Comparison", layout="wide")

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
                st.warning("pipeline.py içinde main() fonksiyonu bulunmuyor.")
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

        fig = go.Figure()
        fig.add_bar(name=p1, x=scores, y=[p1_data[s] for s in scores])
        fig.add_bar(name=p2, x=scores, y=[p2_data[s] for s in scores])
        fig.update_layout(barmode="group")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📋 Detay")
        st.write(df[df["Player"].isin([p1, p2])] )

if __name__ == "__main__":
    main()
