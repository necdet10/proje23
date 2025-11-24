import pandas as pd
import numpy as np
import mlflow
import os
from datetime import datetime

# ------------------------------
# AYARLAR
# ------------------------------
SCORED_INPUT_CSV = 'data/processed/scored_data.csv'
EXPLAINED_VARIANCE_CSV = 'data/processed/explained_variance_ratio.csv'


OUTPUT_RANKINGS_CSV = 'data/processed/player_ranked.csv'
TOP_10_CSV = 'data/processed/top_10_players.csv'
MIDDLE_10_CSV = 'data/processed/middle_10_players.csv'
BOTTOM_10_CSV = 'data/processed/bottom_10_players.csv'
ELITE_CSV = 'data/processed/elite_anomalies.csv'

SELECTED_PCA_COUNT = 7  # En yüksek varyanslı PCA sayısı

# ------------------------------
# ANA FONKSİYON
# ------------------------------
def calculate_player_rankings():
    # 1️⃣ Verileri yükle
    df_scored = pd.read_csv(SCORED_INPUT_CSV)
    df_variance = pd.read_csv(EXPLAINED_VARIANCE_CSV, index_col=0)
    
    # 2️⃣ En yüksek 7 PCA'yı seç
    top_pca = df_variance.nlargest(SELECTED_PCA_COUNT, 'explained_variance_ratio')
    pca_columns = top_pca.index.tolist()
    variance_values = top_pca['explained_variance_ratio'].values
    weights = variance_values / variance_values.sum()
    total_variance_used = variance_values.sum()

    print(f"✓ Seçilen PCA komponenti: {pca_columns}")
    print(f"✓ Ağırlıklar: {weights}")
    print(f"✓ Toplam açıklanan varyans: {total_variance_used:.4f}")

    # 3️⃣ Base score hesapla
    df_scored['base_score'] = 0.0
    for pca, w in zip(pca_columns, weights):
        if pca not in df_scored.columns:
            raise ValueError(f"❌ {pca} sütunu scored_data.csv'de bulunamadı!")
        df_scored['base_score'] += df_scored[pca] * w

    # 4️⃣ LOF ayarlaması
    pca1_median = df_scored['PCA1'].median()
    df_scored['lof_adjustment'] = df_scored.apply(
        lambda row: 1.08 if (row['is_anomaly']==1 and row['PCA1']>pca1_median) 
                    else 0.92 if (row['is_anomaly']==1 and row['PCA1']<=pca1_median)
                    else 1.0,
        axis=1
    )

    # 5️⃣ Final score
    df_scored['final_score'] = df_scored['base_score'] * df_scored['lof_adjustment']

    # 6️⃣ Kategoriler
    elite_anomalies = df_scored[(df_scored['is_anomaly']==1) & (df_scored['PCA1']>pca1_median)]
    weak_anomalies = df_scored[(df_scored['is_anomaly']==1) & (df_scored['PCA1']<=pca1_median)]
    normal_players = df_scored[df_scored['is_anomaly']==0]

    print(f"\n✓ Elite anomaliler: {len(elite_anomalies)}")
    print(f"✓ Zayıf anomaliler: {len(weak_anomalies)}")
    print(f"✓ Normal oyuncular: {len(normal_players)}")

    # 7️⃣ Sıralama
    df_ranked = df_scored.sort_values('final_score', ascending=False).reset_index(drop=True)
    df_ranked['rank'] = df_ranked.index + 1

    # ------------------------------
    # 8️⃣ DOSYALARA KAYIT
    # ------------------------------
    os.makedirs(os.path.dirname(OUTPUT_RANKINGS_CSV), exist_ok=True)
    columns_to_save = [
        'rank', 'Player', 'Pos', 'final_score', 'base_score', 'lof_score', 'is_anomaly'
    ]

    # 8a️⃣ Tüm sıralama
    df_ranked[columns_to_save].to_csv(OUTPUT_RANKINGS_CSV, index=False)

    # 8b️⃣ İlk 10
    df_ranked.head(10)[columns_to_save].to_csv(TOP_10_CSV, index=False)

    # 8c️⃣ Ortadaki 10
    middle_start = len(df_ranked) // 2 - 5
    middle_end = middle_start + 10
    df_ranked.iloc[middle_start:middle_end][columns_to_save].to_csv(MIDDLE_10_CSV, index=False)

    # 8d️⃣ En kötü 10
    df_ranked.tail(10)[columns_to_save].to_csv(BOTTOM_10_CSV, index=False)

    # Elite anomaliler
    elite_anomalies_sorted = elite_anomalies.sort_values('final_score', ascending=False)
    elite_anomalies_sorted.to_csv(ELITE_CSV, index=False)

    print(f"\n✓ Tüm sıralama kaydedildi: {OUTPUT_RANKINGS_CSV}")
    print(f"✓ İlk 10 oyuncu kaydedildi: {TOP_10_CSV}")
    print(f"✓ Ortadaki 10 oyuncu kaydedildi: {MIDDLE_10_CSV}")
    print(f"✓ En kötü 10 oyuncu kaydedildi: {BOTTOM_10_CSV}")
    print(f"✓ Elite anomaliler kaydedildi: {ELITE_CSV}")

    # ------------------------------
    # 9️⃣ MLflow kaydı
    # ------------------------------
    mlflow.set_experiment("Player_Ranking_Evaluation")
    with mlflow.start_run(run_name=f"player_ranking_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
        mlflow.log_param("n_components_used", len(pca_columns))
        mlflow.log_param("pca_components", ",".join(pca_columns))
        mlflow.log_param("total_variance_used", float(total_variance_used))
        mlflow.log_param("elite_bonus", 1.08)
        mlflow.log_param("weak_penalty", 0.92)
        mlflow.log_param("pca1_median_threshold", float(pca1_median))
        mlflow.log_param("elite_count", len(elite_anomalies))
        mlflow.log_param("weak_count", len(weak_anomalies))
        mlflow.log_param("normal_count", len(normal_players))
        
        for pca, w in zip(pca_columns, weights):
            mlflow.log_param(f"weight_{pca}", float(w))
        
        mlflow.log_artifact(OUTPUT_RANKINGS_CSV)
        mlflow.log_artifact(TOP_10_CSV)
        mlflow.log_artifact(MIDDLE_10_CSV)
        mlflow.log_artifact(BOTTOM_10_CSV)
        mlflow.log_artifact(ELITE_CSV)
        
        print("✓ MLflow'a kaydedildi.")

    return df_ranked

# ------------------------------
# Oyuncu detayları
# ------------------------------
def display_player_details(df_ranked, player_name):
    player = df_ranked[df_ranked['Player'].str.contains(player_name, case=False, na=False)]
    if player.empty:
        print(f"❌ '{player_name}' bulunamadı!")
        return
    player = player.iloc[0]
    print(f"\n{'='*60}")
    print(f"🏀 {player['Player']} - {player['Pos']}")
    print(f"{'='*60}")
    print(f"Sıralama: #{player['rank']}")
    print(f"Final Skor: {player['final_score']:.3f}")
    print(f"Base Skor: {player['base_score']:.3f}")
    print(f"LOF Adjustment: {player['lof_adjustment']:.2f}x")
    print(f"LOF Score: {player['lof_score']:.3f}")
    print(f"Anomali: {'✓ Evet' if player['is_anomaly']==1 else '✗ Hayır'}")

# ------------------------------
# Oyuncu karşılaştırma
# ------------------------------
def compare_players(df_ranked, player1, player2):
    p1_data = df_ranked[df_ranked['Player'].str.contains(player1, case=False, na=False)]
    p2_data = df_ranked[df_ranked['Player'].str.contains(player2, case=False, na=False)]
    
    if p1_data.empty or p2_data.empty:
        print(f"❌ Oyuncu bulunamadı!")
        return
    
    p1 = p1_data.iloc[0]
    p2 = p2_data.iloc[0]
    
    print(f"\n{'='*60}")
    print(f"⚔️  {p1['Player']} VS {p2['Player']}")
    print(f"{'='*60}")
    print(f"Rank: #{p1['rank']:>3} vs #{p2['rank']:>3}")
    print(f"Final: {p1['final_score']:>6.3f} vs {p2['final_score']:>6.3f}")

# ------------------------------
# ÇALIŞTIR
# ------------------------------
if __name__ == "__main__":
    print("🏀 NBA Oyuncu Sıralaması Başlıyor...\n")
    df_ranked = calculate_player_rankings()
    
    print("\n✅ Tüm işlemler tamamlandı!\n")
    
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 200)
    pd.set_option('display.colheader_justify', 'center')

    print("\n📋 Tüm Oyuncu Sıralaması:")
    print(df_ranked[['rank', 'Player', 'Pos', 'final_score', 'base_score', 'lof_score', 'is_anomaly']])
