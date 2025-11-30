import os
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# ------------------------------
# AYARLAR
# ------------------------------
INPUT_CSV = "data/processed/clean_data.csv"
FILTERED_CSV = "data/processed/clean_data_filtered.csv"
PCA_OUTPUT_CSV = "data/processed/pca_features.csv"
PCA_LOADINGS_CSV = "data/processed/pca_loadings_sorted.csv"
EXPLAINED_VARIANCE_CSV = "data/processed/explained_variance_ratio.csv"

DROP_COLS = [
    "Team","Year","Age","GS",
    "FG%","3P%","2P%","eFG%","FT%","TRB"
]

# ------------------------------
# ANA FONKSİYON
# ------------------------------
def main():
    os.makedirs("data/processed", exist_ok=True)

    # 1️⃣ Ham veriyi yükle
    df = pd.read_csv(INPUT_CSV)
    print("✓ Ham veri yüklendi:", INPUT_CSV)

    # 2️⃣ Filtreleme → Year=2025, G>=15
    df_filtered = df[(df["Year"] == 2025) & (df["G"] >= 15)].copy()
    print(f"✓ Filtre uygulandı → Satır sayısı: {len(df_filtered)}")

    # 3️⃣ Gereksiz kolonları sil
    df_filtered = df_filtered.drop(columns=[c for c in DROP_COLS if c in df_filtered.columns])
    print("✓ Gereksiz kolonlar çıkarıldı:", DROP_COLS)

    # 4️⃣ Filtrelenmiş veriyi kaydet
    df_filtered.to_csv(FILTERED_CSV, index=False)
    print("✓ clean_data_filtered.csv kaydedildi:", FILTERED_CSV)

    # ------------------------------
    # 5️⃣ PCA için clean_data_filtered.csv kullan
    # ------------------------------
    df_pca_source = pd.read_csv(FILTERED_CSV)

    # Oyuncu bilgileri
    player_info = df_pca_source[["Player", "Pos"]].copy()

    # PCA için sayısal kolonlar
    numeric_df = df_pca_source.drop(columns=["Player", "Pos"])

    # Normalize et
    scaler = StandardScaler()
    numeric_scaled = scaler.fit_transform(numeric_df)
    print("✓ Veriler normalize edildi.")

    # PCA uygula
    pca = PCA()
    pca_values = pca.fit_transform(numeric_scaled)
    print("✓ PCA uygulandı.")
    print("Açıklanan varyans oranları:", pca.explained_variance_ratio_)

    # ------------------------------
    # 6️⃣ PCA features CSV
    # ------------------------------
    pca_df = pd.DataFrame(pca_values, columns=[f"PCA{i+1}" for i in range(pca_values.shape[1])])
    final_pca_df = pd.concat([player_info, pca_df], axis=1)
    final_pca_df.to_csv(PCA_OUTPUT_CSV, index=False)
    print("✓ pca_features.csv kaydedildi:", PCA_OUTPUT_CSV)

    # ------------------------------
    # 7️⃣ PCA loadings CSV – açıklanan varyans olmadan
    # ------------------------------
    sorted_idx = pca.explained_variance_ratio_.argsort()[::-1]
    sorted_components = pca.components_[sorted_idx, :]
    sorted_columns = [f"PCA{i+1}" for i in range(sorted_components.shape[0])]

    loadings_sorted_df = pd.DataFrame(
        sorted_components.T,
        index=numeric_df.columns,
        columns=sorted_columns
    )
    loadings_sorted_df.to_csv(PCA_LOADINGS_CSV)
    print("✓ pca_loadings_sorted.csv kaydedildi (sadece loadings):", PCA_LOADINGS_CSV)

    # ------------------------------
    # 8️⃣ Explained variance CSV
    # ------------------------------
    explained_variance_df = pd.DataFrame(
        pca.explained_variance_ratio_,
        index=[f"PCA{i+1}" for i in range(len(pca.explained_variance_ratio_))],
        columns=["explained_variance_ratio"]
    )
    explained_variance_df.to_csv(EXPLAINED_VARIANCE_CSV)
    print("✓ explained_variance_ratio.csv kaydedildi:", EXPLAINED_VARIANCE_CSV)

# ------------------------------
# ÇALIŞTIR
# ------------------------------
if __name__ == "__main__":
    main()