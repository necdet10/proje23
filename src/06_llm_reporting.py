import streamlit as st
import pandas as pd
import openai
import plotly.graph_objects as go
import os

# ------------------------------
# Sayfa Yapılandırması
# ------------------------------
st.set_page_config(page_title="NBA Player Comparison", layout="wide", page_icon="🏀")

# ------------------------------
# OpenAI API Key
# ------------------------------
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except:
    st.warning("⚠️ OpenAI API key bulunamadı!")
    openai.api_key = None

# ------------------------------
# Dosya Yolları
# ------------------------------
PLAYER_RANKED_CSV = "data/processed/player_ranked.csv"
CLEAN_DATA_CSV = "data/processed/clean_data.csv"
CLEAN_DATA_FILTERED_CSV = "data/processed/clean_data_filtered.csv"
MISSING_REPORT_CSV = "data/processed/missing_value_report.csv"
PCA_TXT_FILE = r"C:\Users\seren\OneDrive\Masaüstü\VisualStudio\Yeni klasör (4)\proje23\pca.txt"
PCA_LOADINGS_CSV = "data/processed/pca_loadings_sorted.csv"
EXPLAINED_VAR_CSV = "data/processed/explained_variance_ratio.csv"
PCA_FEATURES_CSV = "data/processed/pca_features.csv"
LOF_TXT_FILE = r"C:\Users\seren\OneDrive\Masaüstü\VisualStudio\Yeni klasör (4)\proje23\lof.txt"

TOP_10_CSV = "data/processed/top_10_players.csv"
MIDDLE_10_CSV = "data/processed/middle_10_players.csv"
BOTTOM_10_CSV = "data/processed/bottom_10_players.csv"

# ------------------------------
# Veri Yükleme
# ------------------------------
@st.cache_data
def load_data():
    if not os.path.exists(PLAYER_RANKED_CSV):
        st.error(f"❌ {PLAYER_RANKED_CSV} dosyası bulunamadı!")
        st.stop()
    df_ranked = pd.read_csv(PLAYER_RANKED_CSV)
    df_clean = pd.read_csv(CLEAN_DATA_CSV) if os.path.exists(CLEAN_DATA_CSV) else None
    df_clean_filtered = pd.read_csv(CLEAN_DATA_FILTERED_CSV) if os.path.exists(CLEAN_DATA_FILTERED_CSV) else None
    df_missing = pd.read_csv(MISSING_REPORT_CSV) if os.path.exists(MISSING_REPORT_CSV) else None
    return df_ranked, df_clean, df_clean_filtered, df_missing

df_ranked, df_clean, df_clean_filtered, df_missing = load_data()

# ------------------------------
# CLEAN DATA ÖN İZLEME – İlk 15
# ------------------------------
st.subheader("📄 Clean Data – İlk 15 Satır")
if df_clean is not None:
    st.dataframe(df_clean.head(15))
else:
    st.info("Clean data dosyası bulunamadı.")

# ------------------------------
# Eksik Veri Raporu Gösterimi
# ------------------------------
st.subheader("⚠️ Eksik Veri Raporu")
if df_missing is not None:
    st.dataframe(df_missing)
else:
    st.info("Eksik veri raporu bulunamadı.")

# ------------------------------
# CLEAN DATA FILTERED – Sütun İsimleri + İlk 15
# ------------------------------
st.subheader("📄 Clean Data Filtered – Sütun İsimleri")
if df_clean_filtered is not None:
    st.write(" | ".join(list(df_clean_filtered.columns)))
    st.caption("Sadece 2025 yıllarına ait veriler kullanılmıştır. 15 maç altında oynayan oyuncular çıkarılmıştır.")
    st.subheader("📄 Clean Data Filtered – İlk 15 Satır")
    st.dataframe(df_clean_filtered.head(15))
else:
    st.info("Clean data filtered dosyası bulunamadı.")

# ------------------------------
# PCA TXT Dosyası Gösterimi
# ------------------------------
st.subheader("📄 PCA Açıklama Dosyası")
if os.path.exists(PCA_TXT_FILE):
    with open(PCA_TXT_FILE, "r", encoding="utf-8") as f:
        pca_content = f.read()
    st.text_area("PCA İçeriği", value=pca_content, height=300)
else:
    st.info("pca.txt dosyası bulunamadı.")

# ------------------------------
# PCA LOADINGS SORTED CSV
# ------------------------------
st.subheader("📄 PCA Loadings")
if os.path.exists(PCA_LOADINGS_CSV):
    df_loadings = pd.read_csv(PCA_LOADINGS_CSV)
    st.dataframe(df_loadings)
else:
    st.info("pca_loadings_sorted.csv bulunamadı.")

# ------------------------------
# PCA Explained Variance Ratio
# ------------------------------
st.subheader("📈 PCA Explained Variance Ratio ")
if os.path.exists(EXPLAINED_VAR_CSV):
    df_exp = pd.read_csv(EXPLAINED_VAR_CSV)
    st.dataframe(df_exp)
else:
    st.info("explained_variance_ratio.csv bulunamadı.")

# ------------------------------
# PCA Features
# ------------------------------
st.subheader("📄 PCA Features ")
if os.path.exists(PCA_FEATURES_CSV):
    df_features = pd.read_csv(PCA_FEATURES_CSV)
    st.dataframe(df_features)
else:
    st.info("pca_features.csv bulunamadı.")

# ------------------------------
# LOF TXT Dosyası Gösterimi
# ------------------------------
st.subheader("📄 LOF Açıklama Dosyası ")
if os.path.exists(LOF_TXT_FILE):
    with open(LOF_TXT_FILE, "r", encoding="utf-8") as f:
        lof_content = f.read()
    st.markdown(
        f'<textarea readonly style="width:100%;height:300px;font-size:16px;">{lof_content}</textarea>',
        unsafe_allow_html=True
    )
else:
    st.info("lof.txt dosyası bulunamadı.")

# ------------------------------
# TOP / MIDDLE / BOTTOM 10 CSV DOSYALARI
# ------------------------------
st.subheader("📄 Top 10 Oyuncular ")
if os.path.exists(TOP_10_CSV):
    df_top10 = pd.read_csv(TOP_10_CSV)
    st.dataframe(df_top10)
else:
    st.info("top_10_players.csv bulunamadı.")

st.subheader("📄 Middle 10 Oyuncular ")
if os.path.exists(MIDDLE_10_CSV):
    df_middle10 = pd.read_csv(MIDDLE_10_CSV)
    st.dataframe(df_middle10)
else:
    st.info("middle_10_players.csv bulunamadı.")

st.subheader("📄 Bottom 10 Oyuncular ")
if os.path.exists(BOTTOM_10_CSV):
    df_bottom10 = pd.read_csv(BOTTOM_10_CSV)
    st.dataframe(df_bottom10)
else:
    st.info("bottom_10_players.csv bulunamadı.")

# ============================================================
# ORİJİNAL OYUNCU KARŞILAŞTIRMA KODU BURADAN BAŞLIYOR
# ============================================================

st.title("🏀 NBA Oyuncu Karşılaştırma Aracı")
st.markdown("""
**PCA + LOF** modeli kullanılarak oluşturulan oyuncu sıralamalarını karşılaştırın.
İki oyuncu seçin ve detaylı analiz ile GPT-4 yorumunu görün.
""")

# Oyuncu seçimi
st.sidebar.header("🎯 Oyuncu Seçimi")
players = df_ranked['Player'].tolist()
default_p1 = 0
default_p2 = min(1, len(players)-1)
player1_name = st.sidebar.selectbox("Oyuncu 1", players, index=default_p1, key="p1")
player2_name = st.sidebar.selectbox("Oyuncu 2", players, index=default_p2, key="p2")

# Karşılaştırma
if st.sidebar.button("⚔️ Karşılaştır", type="primary", use_container_width=True):
    p1_data = df_ranked[df_ranked['Player'] == player1_name].iloc[0]
    p2_data = df_ranked[df_ranked['Player'] == player2_name].iloc[0]

    # Skor Karşılaştırması
    st.subheader("📊 Skor Karşılaştırması")
    scores = ['final_score', 'base_score', 'lof_score']
    fig = go.Figure(data=[
        go.Bar(
            name=player1_name,
            x=scores,
            y=[p1_data[s] for s in scores],
            marker_color='#1f77b4',
            text=[f"{p1_data[s]:.3f}" for s in scores],
            textposition='auto'
        ),
        go.Bar(
            name=player2_name,
            x=scores,
            y=[p2_data[s] for s in scores],
            marker_color='#ff7f0e',
            text=[f"{p2_data[s]:.3f}" for s in scores],
            textposition='auto'
        )
    ])
    fig.update_layout(
        barmode='group',
        title="Skor Karşılaştırması",
        yaxis_title="Skor",
        xaxis_title="Skor Türü",
        height=400,
        showlegend=True
    )
    st.plotly_chart(fig, use_container_width=True)

    # Detaylı Analiz Tablosu
    st.subheader("📋 Detaylı Karşılaştırma")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### 🔵 {player1_name}")
        data1 = {
            'Metrik': ['Rank', 'Final Score', 'Base Score', 'LOF Score', 'Anomali', 'Pozisyon'],
            'Değer': [
                f"#{p1_data['rank']:.0f}",
                f"{p1_data['final_score']:.4f}",
                f"{p1_data['base_score']:.4f}",
                f"{p1_data['lof_score']:.4f}",
                '✓ Evet' if p1_data['is_anomaly'] == 1 else '✗ Hayır',
                p1_data.get('Pos', 'N/A')
            ]
        }
        st.table(pd.DataFrame(data1))
    with col2:
        st.markdown(f"### 🟠 {player2_name}")
        data2 = {
            'Metrik': ['Rank', 'Final Score', 'Base Score', 'LOF Score', 'Anomali', 'Pozisyon'],
            'Değer': [
                f"#{p2_data['rank']:.0f}",
                f"{p2_data['final_score']:.4f}",
                f"{p2_data['base_score']:.4f}",
                f"{p2_data['lof_score']:.4f}",
                '✓ Evet' if p2_data['is_anomaly'] == 1 else '✗ Hayır',
                p2_data.get('Pos', 'N/A')
            ]
        }
        st.table(pd.DataFrame(data2))

    # Sonuç Hesabı
    st.subheader("🏆 Sonuç")
    winner = player1_name if p1_data['final_score'] > p2_data['final_score'] else player2_name
    score_diff = abs(p1_data['final_score'] - p2_data['final_score'])
    st.success(f"**{winner}** daha iyi performans gösteriyor! (Fark: {score_diff:.4f})")

    # GPT-4 Analizi
    if openai.api_key:
        st.subheader("🤖 GPT-4 Analizi")
        prompt = f"""
İki NBA oyuncusunu karşılaştır ve detaylı analiz yap.

Oyuncu 1: {player1_name}
Rank: {p1_data['rank']}
Final Score: {p1_data['final_score']}
Base Score: {p1_data['base_score']}
LOF Score: {p1_data['lof_score']}
Anomali: {'Evet' if p1_data['is_anomaly']==1 else 'Hayır'}
Pozisyon: {p1_data.get('Pos', 'N/A')}

Oyuncu 2: {player2_name}
Rank: {p2_data['rank']}
Final Score: {p2_data['final_score']}
Base Score: {p2_data['base_score']}
LOF Score: {p2_data['lof_score']}
Anomali: {'Evet' if p2_data['is_anomaly']==1 else 'Hayır'}
Pozisyon: {p2_data.get('Pos', 'N/A')}

1. Genel değerlendirme
2. Güçlü yönler
3. Zayıf yönler
4. Sonuç

Yanıt Türkçe olsun.
"""
        try:
            with st.spinner("GPT-4 analiz yapıyor..."):
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Sen uzman bir NBA veri analisti ve spor yorumcususun."},
                        {"role": "user", "content": prompt}
                    ]
                )
                st.write(response['choices'][0]['message']['content'])
        except Exception as e:
            st.error(f"❌ GPT hatası: {str(e)}")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Toplam Oyuncu**: {len(df_ranked)}")
st.sidebar.markdown(f"**Anomali**: {df_ranked['is_anomaly'].sum()}")
st.sidebar.markdown(f"**Normal**: {(df_ranked['is_anomaly']==0).sum()}")
