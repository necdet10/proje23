import os
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import LocalOutlierFactor
import joblib
import mlflow

# ------------------------------
# AYARLAR
# ------------------------------
PCA_INPUT_CSV = "data/processed/pca_features.csv"
EXPLAINED_VARIANCE_CSV = "data/processed/explained_variance_ratio.csv"
SCORED_OUTPUT_CSV = "data/processed/scored_data.csv"
MODEL_DIR = "models"

N_NEIGHBORS = 20
METRIC = "minkowski"
CONTAMINATION = "auto"
SELECTED_PCA_COUNT = 7  # En yüksek varyanslı PCA sayısı

# ------------------------------
# ANA FONKSİYON
# ------------------------------
def main():
    os.makedirs(MODEL_DIR, exist_ok=True)

    # 1️⃣ PCA verilerini yükle
    df_pca = pd.read_csv(PCA_INPUT_CSV)
    print("✓ PCA verileri yüklendi:", PCA_INPUT_CSV)

    # 2️⃣ Explained variance ratio'yu yükle ve en yüksek 7 PCA seç
    explained_df = pd.read_csv(EXPLAINED_VARIANCE_CSV, index_col=0)
    top_pca_columns = explained_df.sort_values(
        by="explained_variance_ratio", ascending=False
    ).head(SELECTED_PCA_COUNT).index.tolist()
    print(f"✓ En yüksek {SELECTED_PCA_COUNT} varyanslı PCA seçildi:", top_pca_columns)

    # 3️⃣ Sadece seçilen PCA sütunlarını kullan
    for col in top_pca_columns:
        if col not in df_pca.columns:
            raise ValueError(f"PCA column missing in features file: {col}")
    df_features = df_pca[top_pca_columns]

    # 4️⃣ Verileri normalize et
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_features)
    print("✓ PCA verileri normalize edildi.")

    # 5️⃣ LOF modeli oluştur ve fit_predict
    lof = LocalOutlierFactor(
        n_neighbors=N_NEIGHBORS,
        metric=METRIC,
        contamination=CONTAMINATION,
        novelty=False
    )
    lof_labels = lof.fit_predict(X_scaled)  # -1: anomali, 1: normal
    lof_scores = -lof.negative_outlier_factor_  # ters çevrilmiş skor → düşük = iyi

    # 6️⃣ Oyuncu bilgileri + seçilen PCA + LOF sütunları
    player_cols = [col for col in df_pca.columns if not col.startswith("PCA")]
    df_to_save = pd.concat([df_pca[player_cols], df_features], axis=1)
    df_to_save['lof_score'] = lof_scores
    df_to_save['is_anomaly'] = (lof_labels == -1).astype(int)  # 1: anomali, 0: normal

    # 7️⃣ CSV olarak kaydet
    df_to_save.to_csv(SCORED_OUTPUT_CSV, index=False)
    print("✓ LOF skorları ve anomali sütunları kaydedildi:", SCORED_OUTPUT_CSV)

    # ------------------------------
    # 8️⃣ MLflow kaydı
    # ------------------------------
    mlflow.set_experiment("Player_Similarity_LOF")
    with mlflow.start_run():
        # Parametreleri kaydet
        mlflow.log_param("n_neighbors", N_NEIGHBORS)
        mlflow.log_param("metric", METRIC)
        mlflow.log_param("contamination", CONTAMINATION)
        mlflow.log_param("selected_pca_count", SELECTED_PCA_COUNT)
        mlflow.log_param("selected_pca_columns", ",".join(top_pca_columns))
        
        # Metrikler
        mlflow.log_metric("total_players", len(df_to_save))
        mlflow.log_metric("anomaly_count", int(df_to_save['is_anomaly'].sum()))
        mlflow.log_metric("normal_count", int((df_to_save['is_anomaly']==0).sum()))
        mlflow.log_metric("avg_lof_score", float(df_to_save['lof_score'].mean()))

        # Model artifact olarak kaydet
        model_path = os.path.join(MODEL_DIR, "lof_model.joblib")
        joblib.dump(lof, model_path)
        mlflow.log_artifact(model_path, artifact_path="models")
        print("✓ LOF modeli MLflow artifact olarak kaydedildi:", model_path)

        # Scaler artifact olarak kaydet
        scaler_path = os.path.join(MODEL_DIR, "scaler.joblib")
        joblib.dump(scaler, scaler_path)
        mlflow.log_artifact(scaler_path, artifact_path="models")
        print("✓ Scaler MLflow artifact olarak kaydedildi:", scaler_path)

    print("✓ İşlem tamamlandı.")

# ------------------------------
# ÇALIŞTIR
# ------------------------------
if __name__ == "__main__":
    main()