import os
import pytest
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# ------------------------------
# Test Data Paths
# ------------------------------
RAW_DATA = "data/raw/NBA Player Stats and Salaries_2010-2025.csv"
CLEAN_DATA = "data/processed/clean_data.csv"
FILTERED_DATA = "data/processed/clean_data_filtered.csv"
PCA_DATA = "data/processed/pca_features.csv"
SCORED_DATA = "data/processed/scored_data.csv"
RANKED_DATA = "data/processed/player_ranked.csv"

# ------------------------------
# Test 1: Raw Data Exists
# ------------------------------
def test_raw_data_exists():
    """Ham veri dosyasının var olduğunu kontrol et"""
    assert os.path.exists(RAW_DATA), f"❌ Raw data not found: {RAW_DATA}"
    print("✓ Raw data exists")

# ------------------------------
# Test 2: Data Loading
# ------------------------------
def test_data_loading():
    """Veri yüklenebiliyor mu"""
    df = pd.read_csv(RAW_DATA)
    assert not df.empty, "❌ DataFrame is empty"
    assert len(df) > 0, "❌ No rows in DataFrame"
    print(f"✓ Data loaded: {len(df)} rows")

# ------------------------------
# Test 3: Clean Data Integrity
# ------------------------------
def test_clean_data_integrity():
    """Temizlenmiş veri bütünlüğü"""
    if not os.path.exists(CLEAN_DATA):
        pytest.skip(f"Clean data not found: {CLEAN_DATA}")
    
    df = pd.read_csv(CLEAN_DATA)
    
    # Eksik değer kontrolü
    assert df.isna().sum().sum() == 0, "❌ Clean data contains missing values"
    
    # Sütun varlığı kontrolü
    required_cols = ['Player', 'Pos', 'G', 'MP', 'PTS']
    for col in required_cols:
        assert col in df.columns, f"❌ Required column missing: {col}"
    
    print("✓ Clean data integrity passed")

# ------------------------------
# Test 4: Filtered Data Requirements
# ------------------------------
def test_filtered_data():
    """Filtrelenmiş veri gereksinimlerini karşılıyor mu"""
    if not os.path.exists(FILTERED_DATA):
        pytest.skip(f"Filtered data not found: {FILTERED_DATA}")
    
    df = pd.read_csv(FILTERED_DATA)
    
    # G >= 15 kontrolü
    assert (df['G'] >= 15).all(), "❌ Some players have G < 15"
    
    print(f"✓ Filtered data passed: {len(df)} players")

# ------------------------------
# Test 5: PCA Features Validity
# ------------------------------
def test_pca_features():
    """PCA özelliklerinin geçerliliği"""
    if not os.path.exists(PCA_DATA):
        pytest.skip(f"PCA data not found: {PCA_DATA}")
    
    df = pd.read_csv(PCA_DATA)
    
    # PCA sütunlarının varlığı
    pca_cols = [col for col in df.columns if col.startswith('PCA')]
    assert len(pca_cols) > 0, "❌ No PCA columns found"
    
    # Değerlerin sayısal olması
    for col in pca_cols:
        assert pd.api.types.is_numeric_dtype(df[col]), f"❌ {col} is not numeric"
    
    print(f"✓ PCA features valid: {len(pca_cols)} components")

# ------------------------------
# Test 6: LOF Model Output (scored_data.csv)
# ------------------------------
def test_lof_output():
    """LOF model çıktısının doğruluğu - scored_data.csv"""
    if not os.path.exists(SCORED_DATA):
        pytest.skip(f"Scored data not found: {SCORED_DATA}")
    
    df = pd.read_csv(SCORED_DATA)
    
    # scored_data.csv'de olması gerekenler (04_model_training.py çıktısı)
    assert 'lof_score' in df.columns, "❌ lof_score column missing"
    assert 'is_anomaly' in df.columns, "❌ is_anomaly column missing"
    
    # Anomali değerleri (0 veya 1)
    assert df['is_anomaly'].isin([0, 1]).all(), "❌ is_anomaly contains invalid values"
    
    # LOF score pozitif olmalı
    assert (df['lof_score'] > 0).all(), "❌ LOF scores must be positive"
    
    print(f"✓ LOF output valid: {df['is_anomaly'].sum()} anomalies detected")

# ------------------------------
# Test 7: Ranking Consistency (player_ranked.csv)
# ------------------------------
def test_ranking_consistency():
    """Sıralama tutarlılığı - player_ranked.csv"""
    if not os.path.exists(RANKED_DATA):
        pytest.skip(f"Ranked data not found: {RANKED_DATA}")
    
    df = pd.read_csv(RANKED_DATA)
    
    # player_ranked.csv'de olması gerekenler (05_model_evaluation.py çıktısı)
    assert 'final_score' in df.columns, "❌ final_score column missing"
    assert 'rank' in df.columns, "❌ rank column missing"
    assert 'base_score' in df.columns, "❌ base_score column missing"
    
    # Final score sıralı mı (azalan sırada)
    assert df['final_score'].is_monotonic_decreasing, "❌ Final scores not properly sorted"
    
    # Rank kontrolü (1'den başlayarak sıralı)
    expected_ranks = list(range(1, len(df)+1))
    actual_ranks = df['rank'].tolist()
    assert actual_ranks == expected_ranks, "❌ Rank values inconsistent"
    
    print(f"✓ Ranking consistency passed: {len(df)} players ranked")

# ------------------------------
# Test 8: PCA Reconstruction Error
# ------------------------------
def test_pca_reconstruction():
    """PCA yeniden yapılandırma hatası kabul edilebilir mi"""
    if not os.path.exists(FILTERED_DATA) or not os.path.exists(PCA_DATA):
        pytest.skip("Required files not found for reconstruction test")
    
    # Orijinal veri
    df_original = pd.read_csv(FILTERED_DATA)
    numeric_cols = df_original.select_dtypes(include=[np.number]).columns
    X_original = df_original[numeric_cols].values
    
    # Normalize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_original)
    
    # PCA
    pca = PCA(n_components=7)
    X_pca = pca.fit_transform(X_scaled)
    X_reconstructed = pca.inverse_transform(X_pca)
    
    # Yeniden yapılandırma hatası
    mse = np.mean((X_scaled - X_reconstructed) ** 2)
    assert mse < 1.0, f"❌ PCA reconstruction error too high: {mse:.4f}"
    
    print(f"✓ PCA reconstruction MSE: {mse:.4f}")

# ------------------------------
# Test 9: Model Files Exist
# ------------------------------
def test_model_files():
    """Model dosyalarının varlığı"""
    model_files = [
        "models/lof_model.joblib",
        "models/scaler.joblib"
    ]
    
    missing_files = []
    for file in model_files:
        if os.path.exists(file):
            print(f"✓ Model file found: {file}")
        else:
            missing_files.append(file)
    
    if missing_files:
        pytest.skip(f"Model files not found: {missing_files}")

# ------------------------------
# Test 10: Data Consistency Across Pipeline
# ------------------------------
def test_data_consistency():
    """Pipeline boyunca veri tutarlılığı"""
    files = {
        'clean': CLEAN_DATA,
        'filtered': FILTERED_DATA,
        'pca': PCA_DATA,
        'scored': SCORED_DATA,
        'ranked': RANKED_DATA
    }
    
    existing_files = {k: v for k, v in files.items() if os.path.exists(v)}
    
    if len(existing_files) < 2:
        pytest.skip("Not enough files for consistency check")
    
    # Filtreleme sonrası dosyalar aynı satır sayısına sahip olmalı
    if 'filtered' in existing_files and 'pca' in existing_files:
        df_filtered = pd.read_csv(existing_files['filtered'])
        df_pca = pd.read_csv(existing_files['pca'])
        assert len(df_filtered) == len(df_pca), "❌ Filtered and PCA row count mismatch"
    
    if 'pca' in existing_files and 'scored' in existing_files:
        df_pca = pd.read_csv(existing_files['pca'])
        df_scored = pd.read_csv(existing_files['scored'])
        assert len(df_pca) == len(df_scored), "❌ PCA and scored row count mismatch"
    
    if 'scored' in existing_files and 'ranked' in existing_files:
        df_scored = pd.read_csv(existing_files['scored'])
        df_ranked = pd.read_csv(existing_files['ranked'])
        assert len(df_scored) == len(df_ranked), "❌ Scored and ranked row count mismatch"
    
    print("✓ Data consistency across pipeline passed")

# ------------------------------
# Test 11: Output Files Exist
# ------------------------------
def test_output_files():
    """05_model_evaluation.py çıktı dosyalarının varlığı"""
    output_files = [
        "data/processed/player_ranked.csv",
        "data/processed/top_10_players.csv",
        "data/processed/middle_10_players.csv",
        "data/processed/bottom_10_players.csv",
        "data/processed/elite_anomalies.csv"
    ]
    
    missing = []
    for file in output_files:
        if os.path.exists(file):
            print(f"✓ Output file found: {file}")
        else:
            missing.append(file)
    
    if missing:
        pytest.skip(f"Output files not generated yet: {missing}")

# ------------------------------
# Run All Tests
# ------------------------------
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])