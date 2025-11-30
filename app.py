import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
import subprocess
from pathlib import Path

# ------------------------------
# Ortam değişkenleri
# ------------------------------
load_dotenv()

# Proje kök dizini
PROJECT_ROOT = Path(__file__).parent.resolve()
CSV_PATH = PROJECT_ROOT / "data/processed/player_ranked.csv"

# ------------------------------
# CSV yoksa pipeline'ı çalıştır
# ------------------------------
def ensure_csv():
    if not CSV_PATH.exists():
        st.info("player_ranked.csv bulunamadı. Pipeline çalıştırılıyor...")
        try:
            subprocess.run(["python", str(PROJECT_ROOT / "run_pipeline.py")], check=True)
            st.success("Pipeline çalıştı ve CSV oluşturuldu.")
        except Exception as e:
            st.error(f"Pipeline çalıştırılamadı: {e}")
            st.stop()  # CSV yoksa uygulamayı durdur

# ------------------------------
# CSV yükleme fonksiyonu
# ------------------------------
@st.cache_data
def load_ranked_players():
    ensure_csv()  # CSV varsa atlanır, yoksa oluşturulur
    return pd.read_csv(CSV_PATH)

# ------------------------------
# Ana uygulama
# ------------------------------
def main():
    st.set_page_config(page_title="NBA Player Comparison", layout="wide")
    st.title("🏀 NBA Oyuncu Karşılaştırma Aracı")

    # Pipeline butonu (opsiyonel, kullanıcı tekrar çalıştırabilir)
    st.sidebar.subheader("⚙️ Pipeline")
    if st.sidebar.button("Pipeline'ı çalıştır"):
        try:
            subprocess.run(["python", str(PROJECT_ROOT / "run_pipeline.py")], check=True)
            st.success("Pipeline başarıyla çalıştı!")
        except Exception as e:
            st.error(f"Pipeline çalıştırılamadı: {e}")

    df = load_ranked_players()

    players = df["Player"].tolist()
    p1 = st.sidebar.selectbox("Oyuncu 1", players, index=0)
    p2 = st.sidebar.selectbox("Oyuncu 2", players, index=1)

    if st.sidebar.button("Karşılaştır"):
        p1_data = df[df["Player"] == p1].iloc[0]
        p2_data = df[df["Player"] == p2].iloc[0]

        st.subheader("📊 Skor Karşılaştırması")
        scores = ["final_score", "base_score", "lof_score"]

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

# ------------------------------
if __name__ == "__main__":
    main()
