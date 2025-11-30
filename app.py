# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
import subprocess
from pathlib import Path
import traceback

load_dotenv()

# Ayarlar
PROJECT_ROOT = Path(__file__).parent.resolve()
CSV_PATH = PROJECT_ROOT / "data" / "processed" / "player_ranked.csv"
RUN_PIPELINE_PY = PROJECT_ROOT / "run_pipeline.py"

st.set_page_config(page_title="NBA Player Comparison", layout="wide")

# Debug yardımcı: çalışma dizini ve dosyalar
def debug_env():
    st.sidebar.header("Debug")
    st.sidebar.write("Çalışma dizini (cwd):", os.getcwd())
    st.sidebar.write("PROJECT_ROOT:", str(PROJECT_ROOT))
    # show top-level project files for quick check
    try:
        st.sidebar.write("Kök dizin içerik (örnek):", sorted(os.listdir(PROJECT_ROOT))[:30])
    except Exception as e:
        st.sidebar.write("Kök dizin okunamadı:", e)
    st.sidebar.write("CSV beklenen konum:", str(CSV_PATH))
    st.sidebar.write("CSV var mı?:", CSV_PATH.exists())

# CSV yoksa pipeline'ı çalıştır (önce import dene, sonra subprocess)
def ensure_csv(run_via_import=True):
    if CSV_PATH.exists():
        return True

    st.info("player_ranked.csv bulunamadı. Pipeline çalıştırılıyor...")

    # 1) run_pipeline.py import edilip main() varsa çağır
    if run_via_import:
        try:
            import importlib, run_pipeline
            importlib.reload(run_pipeline)
            if hasattr(run_pipeline, "main"):
                st.write("run_pipeline.main() çağırılıyor...")
                run_pipeline.main()
            else:
                st.warning("run_pipeline içinde main() yok — subprocess ile çalıştırılacak.")
                raise RuntimeError("no main()")
        except Exception as e:
            st.write("Import yöntemi ile pipeline çalıştırma başarısız:", e)
            st.write(traceback.format_exc())
            # fallback to subprocess

    # 2) subprocess fallback
    if RUN_PIPELINE_PY.exists():
        try:
            # python executable path kullanmak genelde güvenli
            python_exec = os.sys.executable
            completed = subprocess.run([python_exec, str(RUN_PIPELINE_PY)],
                                       cwd=str(PROJECT_ROOT),
                                       capture_output=True,
                                       text=True,
                                       check=False)
            st.write("Subprocess çıktı (stdout):")
            st.code(completed.stdout or "(stdout boş)")
            st.write("Subprocess hata (stderr):")
            st.code(completed.stderr or "(stderr boş)")
            if completed.returncode != 0:
                st.error(f"run_pipeline.py returncode {completed.returncode}")
                return False
        except Exception as e:
            st.error(f"Subprocess ile pipeline çalıştırılamadı: {e}")
            st.write(traceback.format_exc())
            return False
    else:
        st.error(f"{RUN_PIPELINE_PY} bulunamadı — pipeline dosyası yok.")
        return False

    # son kontrol
    if CSV_PATH.exists():
        st.success("player_ranked.csv oluşturuldu.")
        return True
    else:
        st.error("CSV oluşturulamadı: run_pipeline çıktı verdi ama dosya hala yok.")
        return False

# CSV yükleme
@st.cache_data(show_spinner=False)
def load_ranked_players():
    # Doğrudan CSV'yi okumadan önce mutlak yol güvenliği ve küçük kontroller
    try:
        # debug info: absolute path
        path = CSV_PATH.resolve()
    except Exception:
        path = CSV_PATH

    if not CSV_PATH.exists():
        ok = ensure_csv()
        if not ok:
            # ensure_csv hata mesajlarını zaten gösterdi, burada None dön
            return None

    try:
        df = pd.read_csv(CSV_PATH)
        return df
    except Exception as e:
        st.error(f"CSV okunamadı: {e}")
        st.exception(e)
        return None

# Ana uygulama
def main():
    debug_env()
    st.title("🏀 NBA Oyuncu Karşılaştırma Aracı")

    # Manuel pipeline butonu
    st.sidebar.subheader("⚙️ Pipeline")
    if st.sidebar.button("Pipeline'ı manuel çalıştır"):
        ok = ensure_csv(run_via_import=False)  # test için import denemeleme
        if ok:
            st.success("Pipeline çalıştı (manuel).")
        else:
            st.error("Manuel pipeline çalıştırma başarısız.")

    df = load_ranked_players()
    if df is None:
        st.stop()

    # Basit güvenlik: Player kolonu var mı kontrolü
    if "Player" not in df.columns:
        st.error("CSV içinde 'Player' kolonu bulunamadı. CSV'yi kontrol et.")
        st.write("CSV ilk satırları (preview):")
        try:
            st.dataframe(pd.read_csv(CSV_PATH, nrows=10))
        except Exception as e:
            st.error("CSV preview alınamadı.")
        st.stop()

    players = df["Player"].tolist()
    if len(players) < 2:
        st.warning("En az 2 oyuncu gereklidir (CSV'de yeterli oyuncu yok).")
    p1 = st.sidebar.selectbox("Oyuncu 1", players, index=0 if players else 0)
    p2 = st.sidebar.selectbox("Oyuncu 2", players, index=1 if len(players) > 1 else 0)

    if st.sidebar.button("Karşılaştır"):
        try:
            p1_data = df[df["Player"] == p1].iloc[0]
            p2_data = df[df["Player"] == p2].iloc[0]
        except Exception as e:
            st.error("Seçilen oyuncular CSV'de bulunamadı veya veri eksik.")
            st.exception(e)
            return

        st.subheader("📊 Skor Karşılaştırması")
        scores = ["final_score", "base_score", "lof_score"]
        # Eksik skor kolonlarını kontrol et
        missing_scores = [s for s in scores if s not in df.columns]
        if missing_scores:
            st.error(f"CSV içinde eksik skor kolonları: {missing_scores}")
            st.stop()

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name=p1, x=scores, y=[p1_data[s] for s in scores],
            text=[f"{p1_data[s]:.3f}" for s in scores], textposition="auto"
        ))
        fig.add_trace(go.Bar(
            name=p2, x=scores, y=[p2_data[s] for s in scores],
            text=[f"{p2_data[s]:.3f}" for s in scores], textposition="auto"
        ))
        fig.update_layout(barmode="group", yaxis_title="Skor", xaxis_title="Skor Türü", height=400)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📋 Detaylı Karşılaştırma")
        st.dataframe(df[df["Player"].isin([p1, p2])])

if __name__ == "__main__":
    main()
