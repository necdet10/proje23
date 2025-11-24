import os
import pandas as pd

# ------------------------------
# AYARLAR
# ------------------------------
RAW_DIR = os.path.join("data", "raw")
PROCESSED_DIR = os.path.join("data", "processed")
INPUT_CSV = os.path.join(RAW_DIR, "NBA Player Stats and Salaries_2010-2025.csv")  # kendi CSV adına göre değiştir
OUTPUT_CSV = os.path.join(PROCESSED_DIR, "clean_data.csv")

# ------------------------------
# KLASÖR OLUŞTURMA
# ------------------------------
def ensure_folders():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    print("✓ data/processed klasörü hazır.")

# ------------------------------
# HAM VERİYİ OKU
# ------------------------------
def load_data():
    if not os.path.exists(INPUT_CSV):
        raise FileNotFoundError(f"Ham veri bulunamadı: {INPUT_CSV}")
    df = pd.read_csv(INPUT_CSV)
    print(f"✓ Ham veri yüklendi: {INPUT_CSV}")
    return df

# ------------------------------
# EKSİK VERİ ANALİZİ (CSV KAYITLI)
# ------------------------------
def missing_value_report(df):

    missing_counts = df.isna().sum()
    missing_table = pd.DataFrame({
        'Column': missing_counts.index,
        'MissingValues': missing_counts.values
    })
    missing_table = missing_table[missing_table['MissingValues'] > 0]

    # CSV olarak kaydet
    output_path = os.path.join(PROCESSED_DIR, "missing_value_report.csv")
    missing_table.to_csv(output_path, index=False)

    if missing_table.empty:
        print("✓ Eksik veri yok. (CSV oluşturuldu)")
    else:
        print("\n--- Eksik Veri Raporu ---")
        print(missing_table)
        print(f"\n✓ Eksik veri raporu kaydedildi: {output_path}\n")

    return missing_table


# ------------------------------
# VERİ TEMİZLEME
# ------------------------------
def clean_data(df):
    # Tüm eksik değerleri 0 ile doldur
    df_filled = df.fillna(0)

    # Veri tiplerini düzelt (sayısal kolonlar float/int)
    for col in df_filled.columns:
        if df_filled[col].dtype == 'object':
            try:
                df_filled[col] = pd.to_numeric(df_filled[col])
            except:
                pass  # string kolonları bozma

    print("✓ Eksik değerler 0 ile dolduruldu ve veri tipleri düzenlendi.")
    return df_filled

# ------------------------------
# SÜTUN YERİ DEĞİŞTİRME (Örnek)
# ------------------------------
def swap_columns(df, col1, col2):
    """DataFrame içinde iki sütunun yerini değiştirir."""
    cols = list(df.columns)
    i, j = cols.index(col1), cols.index(col2)
    cols[i], cols[j] = cols[j], cols[i]
    df = df[cols]
    print(f"✓ '{col1}' ve '{col2}' sütunlarının yeri değiştirildi.")
    return df

# ------------------------------
# SÜTUN SIRALAMASI
# ------------------------------
def reorder_columns(df):
    desired_order = [
        'Player', 'Pos',  'Team','Year','Age', 'G', 'GS', 'MP', 'FG', 'FGA', 'FG%',
        '3P', '3PA', '3P%', '2P', '2PA', '2P%', 'eFG%', 'FT', 'FTA', 'FT%',
        'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS'
    ]
    existing_cols = [col for col in desired_order if col in df.columns]
    df = df[existing_cols]
    print("✓ Sütunlar istenilen sıraya göre yeniden düzenlendi.")
    return df

# ------------------------------
# TEMİZ VERİYİ KAYDET
# ------------------------------
def save_data(df):
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✓ Temiz veri kaydedildi: {OUTPUT_CSV}")

# ------------------------------
# ANA FONKSİYON
# ------------------------------
def main():
    print("\n--- NBA Data Cleaning Started ---\n")
    
    ensure_folders()
    df = load_data()
    missing_value_report(df)
    df_clean = clean_data(df)
    
    # Örnek: 'Player' ve 'Team' sütunlarının yerini değiştir
    if "Player" in df_clean.columns and "Team" in df_clean.columns:
        df_clean = swap_columns(df_clean, "Player", "Team")
    
    # İstenen sütun sıralamasını uygula
    df_clean = reorder_columns(df_clean)
    
    save_data(df_clean)
    
    print("\n--- İşlem tamamlandı. ---\n")

if __name__ == "__main__":
    main()

